from flask import Flask, render_template, session, redirect, url_for, request
from flask import logging, g
from settings import users
from functions import fetch_pending_orders_data, fetch_products_data,\
     fetch_suppliers_data, get_user_id, suppDataCheck, suppDataInsert, \
     suppDataUpdate, setActiveTab, appendProduct, checkProduct, throw_product,\
     fetch_invoices_data, removeProduct, getSupplierData, revocateOrder,\
     sendPurchaseOrder, fetch_held_products, checkOTLock, grasp_product,\
     eliminate_product


app = Flask(__name__)


@app.route('/')
def index():
    """Composes operator dashboard"""
    if 'username' in session:
        user = session['username']
        logo = users.get(user).get('img')
    else:
        return redirect(url_for('login'))
    if 'active_tab' not in session:  # active tab defining
        session['active_tab'] = 'orders'  # <-- initial value
    o_dataset, pii_data = fetch_pending_orders_data()  # compose
    otl = checkOTLock()
    agg_products = fetch_products_data(pii_data)  # tabs
    supp_tab_data = fetch_suppliers_data()
    p_invoices_tab_data = fetch_invoices_data('pending')
    sent_PO_tab_data = fetch_invoices_data('sent')
    heldP_tab_data = fetch_held_products()
    a_tab = setActiveTab(session['active_tab'])
    return render_template(
        'index.htm', user=user, logo=logo, orders=o_dataset, o_t_lock=otl,
        orders_agg=agg_products, agg_products_qty=len(agg_products),
        active=a_tab, supp_data=supp_tab_data, pItab=p_invoices_tab_data,
        sItab = sent_PO_tab_data, hTd = heldP_tab_data
        )


@app.route('/login', methods=['GET', 'POST'])
def login():
    """A primitive authentication feature"""
    if request.method == 'POST':
        input_username = request.form['username']
        input_password = request.form['password']
        if (input_username in users and
            users.get(input_username).get('password') == input_password):
            session['username'] = input_username
            session['userID'] = get_user_id(input_username)
            return redirect(url_for('index'))
    return render_template('login.htm')


@app.route('/logout')
def logout():
    """LogOut implementation"""
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/addNewSupplier')
def addS_modal_form():
    """Modal for upload data about a new supplier"""
    app.logger.debug('This is SupplierForm modal')
    sup_data = {'city': 'Sydney', 'province': 'New South Wales'}
    return render_template('addNewSupplierForm.htm', sup_data=sup_data)


@app.route('/editSupplier', methods=['GET'])
def editS_modal_form():
    """Modal for upload data about a new supplier"""
    app.logger.debug('This is editSupplierForm')
    sup_data = getSupplierData(request.args.get('s_id'))
    return render_template('editSupplierForm.htm', sup_data=sup_data)


@app.route('/SupplierDataFiller', methods=['GET', 'POST'])
def supplierDataFill():
    """Manipulation with the input data and redirect"""
    app.logger.debug('This is supplier data filler')
    if request.method == 'POST':
        (pure_data, check_up) = suppDataCheck(request.form)
        if check_up == 'new':
            suppDataInsert(pure_data, session['userID'])
            session['active_tab'] = 'supplier'
        elif check_up == 'known':
            suppDataUpdate(pure_data, session['userID'])
            session['active_tab'] = 'supplier'
        elif check_up == 'update':
            suppDataUpdate(pure_data, session['userID'])
            session['active_tab'] = 'supplier'
    return redirect(url_for('index'))


@app.route('/appendItem', methods=['GET', 'POST'])
def appendItem():
    """Includes product into invoice and redirect"""
    app.logger.debug('This is appendItem to PO process')
    if request.method == 'POST':
        (prod_properties, check_up) = checkProduct(request.form)
        if check_up:
            appendProduct(prod_properties, session['userID'])
    session['active_tab'] = 'p_agg'
    return redirect(url_for('index'))


@app.route('/removeItem', methods=['GET', 'POST'])
def freeItem():
    """Removes product out from invoice and redirect"""
    app.logger.debug('This is freeItem out from PO process')
    if request.method == 'POST':
        removeProduct(session['userID'], request.form['piID'])
    session['active_tab'] = 'invoices'
    return redirect(url_for('index'))


@app.route('/toggleOrder', methods=['GET'])
def toggleOrder():
    """Exclude or include order and its products out from
    processing and redirect to index page"""
    o_id = request.args.get('o_id')
    app.logger.debug('This is revOrder id=%s' % (o_id,))
    revocateOrder(o_id, session['username'])
    session['active_tab'] = 'orders'
    return redirect(url_for('index'))


@app.route('/sendPO', methods=['GET'])
def sendPurOrder():
    """Organize application output"""
    i_id = request.args.get('i_id')
    app.logger.debug('This is send purchase order with id=%s' % (i_id,))
    sendPurchaseOrder(i_id, session['username'])
    session['active_tab'] = 'invoices'
    return redirect(url_for('index'))


@app.route('/graspProduct', methods=['GET'])
def graspProduct():
    """Move product to the pail"""
    sku = request.args.get('p_id')
    app.logger.debug('This is grasp product with sku=%s and userID=%s' %
                     (sku, session['userID']))
    result = grasp_product(sku, session['userID'])
    session['active_tab'] = 'p_agg'
    return redirect(url_for('index'))


@app.route('/throwProduct', methods=['GET'])
def throwProduct():
    """Move product to the agg product tab"""
    pipID = request.args.get('p_id')
    app.logger.debug('This is throw product with ID=%s out from product pail \
     and userID=%s' % (pipID, session['userID']))
    result = throw_product(pipID, session['userID'])
    session['active_tab'] = 'p_agg'
    return redirect(url_for('index'))


@app.route('/eliminateProduct', methods=['GET'])
def eliminateProduct():
    """Move product to the trash"""
    pipID = request.args.get('p_id')
    app.logger.debug('This is eliminate product with ID=%s out from product\
    pail and userID=%s' % (pipID, session['userID']))
    result = eliminate_product(pipID, session['userID'])
    session['active_tab'] = 'p_agg'
    return redirect(url_for('index'))


app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
