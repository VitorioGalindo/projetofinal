import logging
from flask import Blueprint, jsonify, request

from backend.models import db, ResearchNote

logger = logging.getLogger(__name__)
research_bp = Blueprint('research_bp', __name__)


@research_bp.route('/notes', methods=['GET'])
def list_notes():
    try:
        notes = ResearchNote.query.order_by(ResearchNote.last_updated.desc()).all()
        data = [
            {
                'id': n.id,
                'title': n.title,
                'summary': n.summary,
                'content': n.content,
                'last_updated': n.last_updated.isoformat() if n.last_updated else None,
            }
            for n in notes
        ]
        return jsonify({'success': True, 'notes': data})
    except Exception as e:
        logger.error(f'Erro ao listar notas: {e}')
        return jsonify({'success': False, 'error': 'Erro ao listar notas'}), 500


@research_bp.route('/notes', methods=['POST'])
def create_note():
    data = request.get_json(silent=True) or {}
    title = data.get('title')
    summary = data.get('summary', '')
    content = data.get('content', '')
    if not title:
        return jsonify({'success': False, 'error': 'Campos obrigatórios não fornecidos'}), 400
    try:
        note = ResearchNote(title=title, summary=summary, content=content)
        db.session.add(note)
        db.session.commit()
        return (
            jsonify(
                {
                    'success': True,
                    'note': {
                        'id': note.id,
                        'title': note.title,
                        'summary': note.summary,
                        'content': note.content,
                        'last_updated': note.last_updated.isoformat() if note.last_updated else None,
                    },
                }
            ),
            201,
        )
    except Exception as e:
        db.session.rollback()
        logger.error(f'Erro ao criar nota: {e}')
        return jsonify({'success': False, 'error': 'Erro ao criar nota'}), 500


@research_bp.route('/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id: int):
    data = request.get_json(silent=True) or {}
    try:
        note = ResearchNote.query.get(note_id)
        if not note:
            return jsonify({'success': False, 'error': 'Nota não encontrada'}), 404
        if 'title' in data:
            note.title = data['title']
        if 'summary' in data:
            note.summary = data['summary']
        if 'content' in data:
            note.content = data['content']
        db.session.commit()
        return jsonify(
            {
                'success': True,
                'note': {
                    'id': note.id,
                    'title': note.title,
                    'summary': note.summary,
                    'content': note.content,
                    'last_updated': note.last_updated.isoformat() if note.last_updated else None,
                },
            }
        )
    except Exception as e:
        db.session.rollback()
        logger.error(f'Erro ao atualizar nota {note_id}: {e}')
        return jsonify({'success': False, 'error': 'Erro ao atualizar nota'}), 500


@research_bp.route('/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id: int):
    try:
        note = ResearchNote.query.get(note_id)
        if not note:
            return jsonify({'success': False, 'error': 'Nota não encontrada'}), 404
        db.session.delete(note)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        logger.error(f'Erro ao deletar nota {note_id}: {e}')
        return jsonify({'success': False, 'error': 'Erro ao deletar nota'}), 500
