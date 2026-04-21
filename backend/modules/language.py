"""
KrishiBot - Language Detection Module
"""

def detect_language(text: str) -> str:
    hindi_chars = set('अआइईउऊएऐओऔकखगघचछजझटठडढणतथदधनपफबभमयरलवशषसह')
    kannada_chars = set('ಅಆಇಈಉಊಋಎಏಐಒಓಔಕಖಗಘಙಚಛಜಝಞಟಠಡಢಣತಥದಧನಪಫಬಭಮಯರಲವಶಷಸಹ')
    
    text_chars = set(text)
    
    if text_chars & hindi_chars:
        return 'hi'
    elif text_chars & kannada_chars:
        return 'kn'
    return 'en'

def translate_response(text: str, target_lang: str) -> str:
    # Basic translation via MyMemory API (free)
    if target_lang == 'en':
        return text
    try:
        import requests
        lang_map = {'hi': 'hi', 'kn': 'kn'}
        target = lang_map.get(target_lang, 'en')
        url = f"https://api.mymemory.translated.net/get?q={text[:500]}&langpair=en|{target}"
        response = requests.get(url, timeout=5)
        data = response.json()
        if data.get('responseStatus') == 200:
            return data['responseData']['translatedText']
    except:
        pass
    return text
