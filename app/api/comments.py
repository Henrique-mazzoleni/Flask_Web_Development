from flask import request, jsonify, current_app, url_for
from . import api
from ..models import Post, Comment

@api.route('/post/<int:id>/comments/')
def get_post_comments(id):
    page = request.args.get('page', 1, type=int)
    post = Post.query.get_or_404(id)
    pagination = post.comments.paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'], error_out=False)
    comments = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_post_comments', page=page-1, id=id)
    next = None
    if pagination.has_next:
        next = url_for('api.get_post_comments', page=page+1, id=id)
    return jsonify({
        'comments': [comment.to_json() for comment in comments],
        'prev_url': prev,
        'next_url': next,
        'count': pagination.total
    })