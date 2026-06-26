from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import os
import uuid

try:
    from pydub import AudioSegment
except ImportError:
    AudioSegment = None


class MediaProcessor:
    def __init__(self, upload_folder, output_folder):
        self.upload_folder = upload_folder
        self.output_folder = output_folder

    def process_image(self, filename, filter_type):
        input_path = os.path.join(self.upload_folder, filename)

        try:
            img = Image.open(input_path).convert("RGB")
        except Exception:
            return None

        if filter_type == "edge":
            img = img.filter(ImageFilter.CONTOUR)
            img = ImageOps.autocontrast(img)
        elif filter_type == "sketch":
            gray = ImageOps.grayscale(img)
            inverted = ImageOps.invert(gray)
            blurred = inverted.filter(ImageFilter.GaussianBlur(14))
            img = Image.blend(gray, ImageOps.invert(blurred), 0.45).convert("RGB")
        elif filter_type == "invert":
            img = ImageOps.invert(img)
        elif filter_type == "poster":
            img = ImageOps.posterize(ImageEnhance.Color(img).enhance(1.5), 3)
        elif filter_type == "solar":
            img = ImageOps.solarize(ImageEnhance.Contrast(img).enhance(1.25), threshold=128)
        elif filter_type == "emboss":
            img = img.filter(ImageFilter.EMBOSS)
            img = ImageOps.autocontrast(img)
        elif filter_type == "noir":
            img = ImageOps.grayscale(img)
            img = ImageEnhance.Contrast(img).enhance(1.9).convert("RGB")
        elif filter_type == "dream":
            soft = img.filter(ImageFilter.GaussianBlur(6))
            img = Image.blend(ImageEnhance.Color(img).enhance(1.6), soft, 0.38)
        elif filter_type == "ink":
            gray = ImageOps.grayscale(img)
            edges = gray.filter(ImageFilter.FIND_EDGES)
            img = ImageOps.autocontrast(ImageOps.invert(edges)).convert("RGB")
        else:
            img = ImageOps.grayscale(img).convert("RGB")

        output_filename = f"edited_{uuid.uuid4().hex}.png"
        output_path = os.path.join(self.output_folder, output_filename)
        img.save(output_path)
        return output_filename

    def process_audio(self, filename, effect_type):
        if AudioSegment is None:
            raise RuntimeError("pydub is not installed. Add pydub to requirements and reinstall dependencies.")

        input_path = os.path.join(self.upload_folder, filename)
        audio = AudioSegment.from_file(input_path)

        if effect_type == "echo":
            delay = AudioSegment.silent(duration=180)
            echo = delay + audio - 10
            audio = audio.overlay(echo)
        elif effect_type == "slow":
            audio = audio._spawn(audio.raw_data, overrides={
                "frame_rate": int(audio.frame_rate * 0.82)
            }).set_frame_rate(audio.frame_rate)
        elif effect_type == "reverb":
            tail_one = AudioSegment.silent(duration=90) + audio - 9
            tail_two = AudioSegment.silent(duration=180) + audio - 14
            audio = audio.overlay(tail_one).overlay(tail_two)
        else:
            audio = audio.fade_in(500).fade_out(900)

        output_filename = f"edited_audio_{uuid.uuid4().hex}.wav"
        output_path = os.path.join(self.output_folder, output_filename)
        audio.export(output_path, format="wav")
        return output_filename
