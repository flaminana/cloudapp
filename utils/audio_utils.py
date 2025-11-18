from pydub import AudioSegment

def convert_to_mono(input_path, output_path):
    audio = AudioSegment.from_wav(input_path)
    mono_audio = audio.set_channels(1)
    mono_audio.export(output_path, format="wav")