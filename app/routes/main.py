from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import csv
from datetime import datetime
from app import db
from app.models.transaction import UploadedTransaction, AcceptedTransaction, Category
from app.forms.import_form import ImportForm

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    # This will now serve as the dashboard
    return render_template('index.html')

@bp.route('/transactions')
@login_required
def transactions():
    accepted_transactions = AcceptedTransaction.query.filter_by(user_id=current_user.id).all()
    categories = Category.query.all()
    return render_template('transactions.html', transactions=accepted_transactions, categories=categories)

@bp.route('/import', methods=['GET', 'POST'])
@login_required
def import_data():
    form = ImportForm()
    categories = Category.query.all()
    
    if form.validate_on_submit():
        if form.file.data:
            filename = secure_filename(form.file.data.filename)
            upload_folder = current_app.config['UPLOAD_FOLDER']
            file_path = os.path.join(upload_folder, filename)
            form.file.data.save(file_path)
            
            with open(file_path, 'r') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                
                for row_num, row in enumerate(csv_reader, start=2):  # start=2 because row 1 is headers
                    # Skip empty rows
                    if not any(row.values()):
                        continue
                    
                    try:
                        # Check for required fields
                        required_fields = ['Date', 'Transaction Type', 'Description', 'Amount']
                        for field in required_fields:
                            if field not in row:
                                raise ValueError(f"Missing {field} column in CSV")
                            if not row[field].strip() and field != 'Description':
                                raise ValueError(f"Missing {field}")

                        # Parse date
                        date_str = row['Date'].strip()
                        date = datetime.strptime(date_str, '%m/%d/%y').date()
                        
                        # Parse amount
                        amount_str = row['Amount'].strip().replace(',', '')
                        amount = float(amount_str)
                        
                        # Determine if it's a debit or credit
                        if row['Transaction Type'] in ['DEBIT', 'ATM DEBIT']:
                            amount = -abs(amount)  # Make sure it's negative for debits
                        
                        # Set description to "Check" if empty and Transaction Type is "CHECK" or "Check"
                        description = row['Description'].strip()
                        if not description and row['Transaction Type'].lower() == 'check':
                            description = "Check"
                        
                        transaction = UploadedTransaction(
                            date=date,
                            transaction_type=row['Transaction Type'],
                            account_type=row.get('Account Type', ''),  # Use get() to handle optional fields
                            description=description,
                            amount=amount,
                            reference_no=row.get('Reference No.', ''),
                            user_id=current_user.id
                        )
                        db.session.add(transaction)
                    except (ValueError, KeyError) as e:
                        flash(f'Error processing row {row_num}: {e}', 'danger')
                        db.session.rollback()
                        return redirect(url_for('main.import_data'))
                
                db.session.commit()
            
            # Create old_uploads directory if it doesn't exist
            old_uploads_dir = os.path.join(upload_folder, 'old_uploads')
            os.makedirs(old_uploads_dir, exist_ok=True)
            
            # Move the file to old_uploads directory
            new_file_path = os.path.join(old_uploads_dir, filename)
            os.rename(file_path, new_file_path)
            
            flash('File uploaded, processed successfully, and moved to old_uploads directory', 'success')
            return redirect(url_for('main.import_data'))

    uploaded_transactions = UploadedTransaction.query.filter_by(user_id=current_user.id).all()
    return render_template('import.html', form=form, transactions=uploaded_transactions, categories=categories)

@bp.route('/api/update_transaction', methods=['POST'])
@login_required
def update_transaction():
    data = request.json
    transaction = UploadedTransaction.query.get(data['id'])
    if transaction and transaction.user_id == current_user.id:
        for key, value in data.items():
            if key != 'id':
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

# @bp.route('/api/accept_transactions', methods=['POST'])
# @login_required
# def accept_transactions():
#     uploaded_transactions = UploadedTransaction.query.filter_by(user_id=current_user.id, include=True).all()
#     for ut in uploaded_transactions:
#         at = AcceptedTransaction(
#             date=ut.date,
#             description=ut.description,
#             amount=ut.amount,
#             category_id=ut.category_id,
#             user_id=ut.user_id
#         )
#         db.session.add(at)
#     UploadedTransaction.query.filter_by(user_id=current_user.id).delete()
#     db.session.commit()
#     flash('Transactions accepted successfully', 'success')
#     return jsonify({'status': 'success'})

@bp.route('/api/accept_transactions', methods=['POST'])
@login_required
def accept_transactions():
    uploaded_transactions = UploadedTransaction.query.filter_by(user_id=current_user.id, include=True).all()
    for ut in uploaded_transactions:
        at = AcceptedTransaction(
            date=ut.date,
            transaction_type=ut.transaction_type,
            account_type=ut.account_type,
            description=ut.description,
            amount=ut.amount,
            reference_no=ut.reference_no,
            category_id=ut.category_id,
            user_id=ut.user_id
        )
        db.session.add(at)
    UploadedTransaction.query.filter_by(user_id=current_user.id).delete()
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
