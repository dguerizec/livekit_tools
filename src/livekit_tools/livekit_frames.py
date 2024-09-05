# import asyncio
# import logging
# import time
# from asyncio import Future
# from signal import SIGINT, SIGTERM
#
# import cv2
# import livekit  # type: ignore[import]
# import livekit.rtc
# import numpy as np
#
# from .livekit_token import create_access_token
# from .livekit_url import parse_livekit_url
#
# window_threads_started = False
#
#
# async def display_livekit_frames(livekit_q: asyncio.Queue[livekit.rtc.VideoFrame], track_id: str) -> None:
#    cv2.namedWindow(f"livekit_{track_id}", cv2.WINDOW_AUTOSIZE)
#    global window_threads_started
#    if not window_threads_started:
#        window_threads_started = True
#        cv2.startWindowThread()
#
#    argb_frame: livekit.rtc.ArgbFrame | None = None
#
#    now = time.time()
#    frame_count = 0
#    t = 1
#
#    try:
#        while cv2.waitKey(1) & 0xFF != ord("q"):
#            frame: livekit.VideoFrame = await livekit_q.get()
#            buffer = frame.buffer
#
#            if argb_frame is None or argb_frame.width != buffer.width or argb_frame.height != buffer.height:
#                argb_frame = livekit.ArgbFrame(livekit.VideoFormatType.FORMAT_ABGR, buffer.width, buffer.height)
#
#            buffer.to_argb(argb_frame)
#
#            arr = np.ctypeslib.as_array(argb_frame.data)
#            arr = arr.reshape((argb_frame.height, argb_frame.width, 4))
#            arr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
#
#            if time.time() - now > t:
#                now = time.time()
#                logging.info(f"fps: {frame_count / t} shape: {arr.shape}")
#                frame_count = 0
#            frame_count += 1
#
#            cv2.imshow(f"livekit_{track_id}", arr)
#
#    finally:
#        cv2.destroyWindow(f"livekit_{track_id}")
#        cv2.waitKey(1)
#
#
# async def run_peek_task(url: str) -> None:
#    flag: Future[bool] = asyncio.Future()
#    peek_task = asyncio.create_task(setup_connection(url, flag))
#    logging.info("waiting for connection")
#    await flag
#    logging.info("connection established")
#    await peek_task
#    logging.info("connection closed")
#
#
# class TrackContext:
#    track_id: str
#    stream: livekit.VideoStream
#    queue: asyncio.Queue[livekit.VideoFrame]
#    display_task: asyncio.Task[None]
#
#    def __init__(self, track_id: str, stream: livekit.VideoStream) -> None:
#        self.track_id = track_id
#        self.stream = stream
#        self.queue = asyncio.Queue()
#        loop = asyncio.get_event_loop()
#        self.display_task = loop.create_task(display_livekit_frames(self.queue, self.track_id))
#
#    def put(self, frame: livekit.VideoFrame) -> None:
#        self.queue.put_nowait(frame)
#
#    async def stop(self) -> None:
#        self.display_task.cancel()
#        await self.display_task
#        self.stream.disconnect()
#
#
# async def setup_connection(url: str, flag: Future[bool]) -> None:
#    room = livekit.Room()
#    info = parse_livekit_url(url)
#    logging.info(info)
#    info["token"] = create_access_token(
#        api_key=info["api_key"], api_secret=info["api_secret"], room_name=info["room"], identity=info["identity"]
#    )
#    logging.info(info)
#
#    options = livekit.RoomOptions(auto_subscribe=True, dynacast=True)
#    try:
#        await room.connect(info["url"], info["token"], options=options)
#
#        logging.info("connected to room: " + room.name)
#
#        tracks: dict[str, TrackContext] = {}
#
#        @room.on("track_subscribed")  # type: ignore[misc]  # decorator
#        def on_track_subscribed(
#            track: livekit.Track, publication: livekit.RemoteTrackPublication, participant: livekit.RemoteParticipant
#        ) -> None:
#            logging.info("track subscribed: %s", track.sid)
#            if track.kind == livekit.TrackKind.KIND_VIDEO:
#                video_stream = livekit.VideoStream(track)
#                context = TrackContext(track.sid, video_stream)
#
#                @video_stream.on("frame_received")  # type: ignore[misc]  # decorator
#                def on_video_frame(frame: livekit.VideoFrame) -> None:
#                    context.put(frame)
#
#                tracks[track.sid] = context
#
#        @room.on("track_unsubscribed")  # type: ignore[misc]  # decorator
#        def on_track_unsubscribed(
#            track: livekit.Track, publication: livekit.RemoteTrackPublication, participant: livekit.RemoteParticipant
#        ) -> None:
#            if track.kind == livekit.TrackKind.KIND_VIDEO:
#                context = tracks[track.sid]
#                context.stream.disconnect()
#                del tracks[track.sid]
#
#        logging.info("connected to room: " + room.name)
#        flag.set_result(True)
#        try:
#            await room.run()
#        except asyncio.CancelledError:
#            logging.info("closing the room")
#            await room.disconnect()
#    except Exception as e:
#        logging.exception(f"failed to connect to room {e}")
#        flag.set_result(False)
#
#
# def peek_on_livekit(url: str = "livekit://localhost/test-room") -> None:
#    logging.basicConfig(level=logging.DEBUG, format="PEEK: %(asctime)s %(levelname)s %(message)s")
#    logging.info("peeking on %s", url)
#    loop = asyncio.get_event_loop()
#    main_task = asyncio.ensure_future(run_peek_task(url))
#    for signal in [SIGINT, SIGTERM]:
#        loop.add_signal_handler(signal, main_task.cancel)
#    loop.run_until_complete(main_task)
#
