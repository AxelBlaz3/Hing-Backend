import os
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from pathlib import Path
import ffmpeg_streaming
from ffmpeg_streaming import Formats


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4'}
VIDEO_EXTENSIONS = {'mp4'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_file(upload_folder: str, upload_type: str, _id: str, file: FileStorage):
    filename = secure_filename(file.filename)
    parent_path = os.path.join(upload_folder, upload_type, _id)
    save_path = os.path.join(parent_path, filename)
    # parent_path = Path(save_path).parent
    if not os.path.exists(parent_path):
        os.makedirs(parent_path)

    file.save(save_path)

    if upload_type == 'videos': 
        video = ffmpeg_streaming.input(save_path)
        dash = video.dash(Formats.h264())
        dash.auto_generate_representations()
        video_name_with_ext = '{}.{}'.format(file.filename.rsplit('.', 1)[0], 'mpd')
        dash.output(parent_path + '/{}'.format(video_name_with_ext))
        os.remove(path=save_path)
        return os.path.join(upload_folder, upload_type, _id, video_name_with_ext)

    return save_path   
