import requests
import os

BASE_URL = 'https://brainboostv2-production.up.railway.app/api'

# Login first
login = requests.post(f'{BASE_URL}/auth/login', json={
    'username': 'admin',
    'password': 'admin123'
})
print(login.json())
token = login.json()['token']
headers = {'Authorization': f'Bearer {token}'}
print(f'Logged in! Token: {token[:20]}...')

# Images to upload — section_id : image_file
images = {
    1: r'C:\Users\Asus\Downloads\iks.jpg.jpeg',
    2: r'C:\Users\Asus\Downloads\computer.webp',
    3: r'C:\Users\Asus\Downloads\english.jpg.jpeg',
    4: r'C:\Users\Asus\Downloads\environment.jpg',
    5: r'C:\Users\Asus\Downloads\cultural.webp',
    6: r'C:\Users\Asus\Downloads\sports.webp',
    7: r'C:\Users\Asus\Downloads\sociopolitical.jpg.jpeg',
}
for section_id, image_path in images.items():
    if os.path.exists(image_path):
        with open(image_path, 'rb') as f:
            ext = image_path.split('.')[-1]
            mime = 'image/jpeg' if ext in ['jpg','jpeg'] else f'image/{ext}'
            files = {'image': (os.path.basename(image_path), f, mime)}
            res = requests.post(
                f'{BASE_URL}/sections/{section_id}/image',
                headers=headers,
                files=files
            )
            print(f'Section {section_id}: {res.json()}')
    else:
        print(f'Section {section_id}: File not found — {image_path}')