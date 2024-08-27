from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import csv
import json
from datetime import datetime
import os
from app import db, cat_man
from app.models.transaction import UploadedTransaction, AcceptedTransaction
from app.forms.import_form import ImportForm

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    return render_template('index.html')

@bp.route('/transactions')
@login_required
def transactions():
    accepted_transactions = AcceptedTransaction.query.filter_by(user_id=current_user.id).all()
    categories = cat_man.get_all_categories_str()
    return render_template('transactions.html', transactions=accepted_transactions, categories=categories)

@bp.route('/import', methods=['GET', 'POST'])
@login_required
def import_data():
    form = ImportForm()
    
    if form.validate_on_submit():
        if form.file.data:
            filename = secure_filename(form.file.data.filename)
            upload_folder = current_app.config['UPLOAD_FOLDER']
            file_path = os.path.join(upload_folder, filename)
            form.file.data.save(file_path)
            
            with open(file_path, 'r') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                
                for row in csv_reader:
                    # Skip empty rows
                    if not any(row.values()):
                        continue
                    try:
                        date = datetime.strptime(row['Date'], '%m/%d/%y').date()
                        # date = datetime.strptime(row['date'], '%Y-%m-%d').date()
                        amount = float(row['Amount'].replace(',', ''))
                        
                        transaction = UploadedTransaction(
                            date=date,
                            transaction_type=row['Transaction Type'],
                            account_type=row.get('Account Type', ''),
                            description=row['Description'],
                            amount=amount,
                            reference_no=row.get('Reference No.', ''),
                            user_id=current_user.id
                        )
                        db.session.add(transaction)
                    except Exception as e:
                        flash(f'Error processing row: {e}', 'error')
                        db.session.rollback()
                        return redirect(url_for('main.import_data'))
                
                db.session.commit()
            
            flash('File uploaded and processed successfully', 'success')
            return redirect(url_for('main.import_data'))

    uploaded_transactions = UploadedTransaction.query.filter_by(user_id=current_user.id).all()
    categories = cat_man.get_all_categories_str()
    return render_template('import.html', form=form, transactions=uploaded_transactions, categories=categories)

@bp.route('/static', methods=['GET', 'POST'])
@login_required
def static_page():
    categories_file_path = cat_man.json_file_path
    rules_file_path = os.path.join(current_app.root_path, 'static', 'ref', 'rules.json')

    if request.method == 'POST':
        if 'save_categories' in request.form:
            categories_data = request.form['categories_data']
            try:
                # Validate JSON
                json.loads(categories_data)
                with open(categories_file_path, 'w') as f:
                    f.write(categories_data)
                cat_man.load_categories()  # Reload categories in memory
                flash('Categories have been saved and reloaded.', 'success')
            except json.JSONDecodeError:
                flash('Invalid JSON format for categories. Please check your input.', 'error')

        elif 'reload_categories' in request.form:
            cat_man.load_categories()
            flash('Categories have been reloaded.', 'success')

        elif 'save_rules' in request.form:
            rules_data = request.form['rules_data']
            try:
                # Validate JSON
                json.loads(rules_data)
                with open(rules_file_path, 'w') as f:
                    f.write(rules_data)
                flash('Rules have been saved.', 'success')
            except json.JSONDecodeError:
                flash('Invalid JSON format for rules. Please check your input.', 'error')

        elif 'reload_rules' in request.form:
            flash('Rules have been reloaded.', 'success')

    # Get fresh data
    categories = cat_man.get_raw_json()
    with open(rules_file_path, 'r') as rules_file:
        rules = rules_file.read()

    return render_template('static.html', categories=categories, rules=rules)

@bp.route('/api/update_transaction', methods=['POST'])
@login_required
def update_transaction():
    data = request.json
    transaction = UploadedTransaction.query.get(data['id'])
    if transaction and transaction.user_id == current_user.id:
        for key, value in data.items():
            if key != 'id':
                if key == 'date':
                    # Convert the date string to a Python date object
                    value = datetime.strptime(value, '%Y-%m-%d').date()
                setattr(transaction, key, value)
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'}), 400

@bp.route('/api/clear_uploaded_transactions', methods=['POST'])
@login_required
def clear_uploaded_transactions():
    UploadedTransaction.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    return jsonify({'status': 'success'})

@bp.route('/api/accept_transactions', methods=['POST'])
@login_required
def accept_transactions():
    data = request.json
    transaction_ids = data.get('transactions', [])
    print("Server side view of transactions to be accepted: ", transaction_ids)
    
    for transaction_id in transaction_ids:
        ut = UploadedTransaction.query.filter_by(id=transaction_id, user_id=current_user.id).first()
        if ut:
            at = AcceptedTransaction(
                date=ut.date,
                transaction_type=ut.transaction_type,
                account_type=ut.account_type,
                description=ut.description,
                amount=ut.amount,
                reference_no=ut.reference_no,
                category_l1=ut.category_l1,
                category_l2=ut.category_l2,
                category_l3=ut.category_l3,
                user_id=ut.user_id,
                applied_rules=ut.applied_rules
            )
            db.session.add(at)
            db.session.delete(ut)
    
    db.session.commit()
    flash('Transactions accepted successfully', 'success')
    return jsonify({'status': 'success'})

@bp.route('/api/delete_all_transactions', methods=['POST'])
@login_required
def delete_all_transactions():
    AcceptedTransaction.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    flash('All accepted transactions have been deleted successfully', 'success')
    return jsonify({'status': 'success'})