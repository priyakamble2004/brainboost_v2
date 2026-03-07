from flask import Blueprint, request, jsonify, send_from_directory, current_app
from models import Section, Level
from database import db
from routes.auth import token_required
import os, uuid

sections_bp  = Blueprint('sections', __name__)
LEVEL_NAMES  = {1:'Beginner', 2:'Easy', 3:'Medium', 4:'Hard', 5:'Expert'}


def allowed_file(filename):
    return ('.' in filename and
            filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS'])


@sections_bp.route('/', methods=['GET'])
def get_sections():
    """GET /api/sections/  →  { sections: [...] }"""
    sections = Section.query.order_by(Section.id).all()
    return jsonify({'sections': [s.to_dict() for s in sections]})


@sections_bp.route('/<int:section_id>', methods=['GET'])
def get_section(section_id):
    """GET /api/sections/<id>  →  { section }"""
    s = Section.query.get_or_404(section_id)
    return jsonify({'section': s.to_dict()})


@sections_bp.route('/<int:section_id>/image', methods=['GET'])
def get_image(section_id):
    """GET /api/sections/<id>/image  →  image file"""
    s = Section.query.get_or_404(section_id)
    if not s.image_path:
        return jsonify({'error': 'No image uploaded for this section'}), 404
    folder   = current_app.config['UPLOAD_FOLDER']
    filename = os.path.basename(s.image_path)
    return send_from_directory(folder, filename)


@sections_bp.route('/<int:section_id>/image', methods=['POST'])
@token_required
def upload_image(current_user, section_id):
    """POST /api/sections/<id>/image  (multipart/form-data, field: image)"""
    s = Section.query.get_or_404(section_id)
    if 'image' not in request.files:
        return jsonify({'error': 'No file in request (field name must be "image")'}), 400
    file = request.files['image']
    if not file.filename:
        return jsonify({'error': 'Empty filename'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed (use png, jpg, jpeg, gif, webp)'}), 400

    # Remove old image if it exists
    if s.image_path and os.path.exists(s.image_path):
        os.remove(s.image_path)

    ext      = file.filename.rsplit('.', 1)[1].lower()
    filename = f'section_{section_id}_{uuid.uuid4().hex}.{ext}'
    os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    s.image_path = filepath
    db.session.commit()
    return jsonify({
        'message':   'Image uploaded successfully',
        'image_url': f'/api/sections/{section_id}/image'
    })
