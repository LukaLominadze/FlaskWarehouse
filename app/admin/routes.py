from datetime import date
from flask import render_template, redirect, url_for, request, flash
from app.admin import bp
from app.admin.forms import AdminCreateUserForm, AdminEditUserForm, AdminResetPasswordForm
from app.models import db, User, Product, Supplier, StockMovement
from app.auth.decorators import admin_required


@bp.route('/')
@admin_required
def admin_dashboard():
    user_count = User.query.count()
    admin_count = User.query.filter_by(is_admin=True).count()
    product_count = Product.query.count()
    supplier_count = Supplier.query.count()
    movement_count = StockMovement.query.count()
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    return render_template('admin/dashboard.html',
                           user_count=user_count,
                           admin_count=admin_count,
                           product_count=product_count,
                           supplier_count=supplier_count,
                           movement_count=movement_count,
                           recent_users=recent_users)


@bp.route('/users')
@admin_required
def user_list():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    query = User.query
    if search:
        like = f'%{search}%'
        query = query.filter(
            db.or_(User.username.ilike(like), User.email.ilike(like))
        )
    pagination = query.order_by(User.id).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('admin/user_list.html',
                           users=pagination.items,
                           pagination=pagination,
                           search=search)


@bp.route('/users/new', methods=['GET', 'POST'])
@admin_required
def user_create():
    form = AdminCreateUserForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            is_admin=form.is_admin.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'User "{user.username}" created.', 'success')
        return redirect(url_for('admin.user_list'))
    return render_template('admin/user_form.html', form=form, title='Create User')


@bp.route('/users/<int:user_id>')
@admin_required
def user_detail(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('admin/user_detail.html', user=user)


@bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def user_edit(user_id):
    user = User.query.get_or_404(user_id)
    form = AdminEditUserForm(
        original_username=user.username,
        original_email=user.email,
        obj=user,
    )
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.is_admin = form.is_admin.data
        db.session.commit()
        flash(f'User "{user.username}" updated.', 'success')
        return redirect(url_for('admin.user_detail', user_id=user.id))
    return render_template('admin/user_form.html', form=form,
                           title=f'Edit User: {user.username}', user=user)


@bp.route('/users/<int:user_id>/reset-password', methods=['GET', 'POST'])
@admin_required
def user_reset_password(user_id):
    user = User.query.get_or_404(user_id)
    form = AdminResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(f'Password reset for "{user.username}".', 'success')
        return redirect(url_for('admin.user_detail', user_id=user.id))
    return render_template('admin/user_form.html', form=form,
                           title=f'Reset Password: {user.username}', user=user)


@bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def user_delete(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        admin_count = User.query.filter_by(is_admin=True).count()
        if admin_count <= 1:
            flash('Cannot delete the last admin account.', 'danger')
            return redirect(url_for('admin.user_list'))
    from flask import session
    if user.id == session.get('user_id'):
        flash('Cannot delete your own account.', 'danger')
        return redirect(url_for('admin.user_list'))
    username = user.username
    db.session.delete(user)
    db.session.commit()
    flash(f'User "{username}" deleted.', 'success')
    return redirect(url_for('admin.user_list'))


@bp.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
@admin_required
def user_toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    from flask import session
    if user.id == session.get('user_id') and user.is_admin:
        flash('Cannot remove your own admin privileges.', 'danger')
        return redirect(url_for('admin.user_list'))
    if not user.is_admin:
        user.is_admin = True
        flash(f'"{user.username}" is now an admin.', 'success')
    else:
        admin_count = User.query.filter_by(is_admin=True).count()
        if admin_count <= 1:
            flash('Cannot remove the last admin account.', 'danger')
            return redirect(url_for('admin.user_list'))
        user.is_admin = False
        flash(f'"{user.username}" is no longer an admin.', 'success')
    db.session.commit()
    return redirect(url_for('admin.user_detail', user_id=user.id))
