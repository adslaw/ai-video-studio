import uuid

def content_to_entities(proj, content):
    proj['content_json'] = content
    proj['selected_hook'] = content.get('hook')
    proj['caption'] = content.get('caption')
    proj['keywords'] = content.get('keywords', [])
    proj['hashtags'] = content.get('hashtags', [])
    scenes = content.get('scenes', [])
    proj['scenes'] = []
    for s in scenes:
        proj['scenes'].append({
            'id': str(uuid.uuid4()),
            'order': s.get('order', 1),
            'narration': s.get('narration', ''),
            'visual_prompt': s.get('visual_prompt', ''),
            'status': 'draft',
            'motion': 'none',
            'image_path': None
        })
    return proj
