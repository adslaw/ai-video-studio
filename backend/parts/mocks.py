import json, io, wave

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

class MockLLM:
    async def chat(self, messages, model, response_format=None):
        return json.dumps({
            'title': 'Amazing Ocean Facts',
            'hook': 'What if the largest animal ever actually lives right now?',
            'narration': 'The blue whale can grow over 30 meters long and weigh up to 180 tons.',
            'cta': 'Follow for more fascinating facts.',
            'caption': 'Dive into the giants of the ocean! #ocean #facts',
            'keywords': ['blue whale', 'ocean facts', 'marine life'],
            'hashtags': ['#ocean', '#facts', '#whale'],
            'scenes': [
                {'order': 1, 'narration': 'The blue whale is the largest animal ever known.', 'visual_prompt': 'giant blue whale swimming'},
                {'order': 2, 'narration': 'Its heart alone weighs as much as a car.', 'visual_prompt': 'whale heart anatomy'},
                {'order': 3, 'narration': 'Its call travels hundreds of kilometers.', 'visual_prompt': 'whale sound waves'}
            ]
        })

class MockImage:
    async def generate(self, prompt, model, size='1024x1792'):
        if HAS_PIL:
            img = Image.new('RGB', (1080, 1920), (10, 30, 60))
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            return buf.getvalue()
        return b'\x89PNG\r\n\x1a\n' + b'\x00' * 100

class MockTTS:
    async def synthesize(self, text, model, language):
        duration = max(3, len(text) // 12)
        sr = 24000
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(b'\x00\x00' * (sr * duration))
        return buf.getvalue()

llm = MockLLM()
img_gen = MockImage()
tts_gen = MockTTS()
