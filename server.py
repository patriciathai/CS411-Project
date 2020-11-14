
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

DATABASEURI = "postgresql://ncp2132:patricianicole@34.75.150.200/proj1part2"

engine = create_engine(DATABASEURI)

@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass

@app.route('/')
def home():
  return render_template('home.html')







############################# CUSTOMER ####################################

@app.route('/customer')
def get_customer():
  return render_template('customer.html')

@app.route("/customer_login", methods=['POST'] )
def customer_login():
  name = request.form['l_name']
  email = request.form['l_email']
  name = "'"+name+"'"
  email = "'"+email+"'"

  cursor = g.conn.execute("SELECT cid FROM customer WHERE c_email={email} AND c_name={name}".format(email=email, name=name))
  list_cid = []
  for result in cursor:
    list_cid.append(result[0])
  cursor.close()
  cid = list_cid[0]

  url = '/customer_main/' + cid
  return redirect(url)

@app.route("/customer_signup")
def customer_signup():
  return render_template('customer_signup.html')

@app.route("/add_customer", methods=['POST'])
def add_customer():
  #This retrieves most recent customer id in the customer table, which lets us assign an id to a new customer
  cursor = g.conn.execute("SELECT cid FROM customer ORDER BY cid DESC LIMIT 1")
  last_cid = []
  for result in cursor:
      last_cid.append(result[0])
  cursor.close()

  name = request.form['s_name']
  email = request.form['s_email']
  phone = request.form['s_phone']
  cid = str(int(last_cid[0]) + 1).zfill(5)
  g.conn.execute('INSERT INTO customer VALUES (%s, %s, %s, %s)', cid, email, phone, name)

  number = request.form['number']
  street = request.form['street']
  apt = request.form['apt']
  zip_code = request.form['zip']
  city = request.form['city']
  state = request.form['state']
  g.conn.execute('INSERT INTO address VALUES (%s, %s, %s, %s, %s, %s)', number, street, apt, zip_code, city, state)
  g.conn.execute('INSERT INTO lives_in VALUES (%s, %s, %s, %s, %s)', cid, number, street, apt, zip_code)

  card_num = request.form['card_num']
  exp = request.form['exp']
  sec = request.form['sec']
  g.conn.execute('INSERT INTO payment_method VALUES (%s, %s, %s)', card_num, exp, sec)
  g.conn.execute('INSERT INTO pays_with VALUES (%s, %s)', cid, card_num)

  url = '/customer_main/' + cid
  return redirect(url)

@app.route("/customer_main/<cid>")
def customer_main(cid):
  string_cid = "'"+cid+"'"
  cursor = g.conn.execute("SELECT c_name FROM customer WHERE cid={string_cid}".format(string_cid=string_cid))
  c_names = []
  for result in cursor:
    c_names.append(result[0])
  cursor.close()
  c_name = c_names[0]

  return render_template('customer_main.html', cid = cid, c_name = c_name)

@app.route("/<cid>/customer_orders")
def customer_orders(cid):
  string_cid = "'"+cid+"'"
  
  #Get all orders for cid
  cursor = g.conn.execute("SELECT O.oid, O.m_name, O.quantity, O.rid FROM order_has_menu_item O, places P WHERE O.oid=P.oid AND P.cid={string_cid}".format(string_cid=string_cid))
  c_orders = []
  for result in cursor:
    c_orders.append(result)
  cursor.close()
  
  unique_oid = [] #this will let us store just distinct oid's
  upcoming = []
  past = []
  
  #iterate through c_orders to get info for all upcoming and past orders
  for row in c_orders:
    if row['oid'] in unique_oid: #if we already have the info for this oid, move on to the next one
      continue
    else:
      unique_oid.append(row['oid'])
      string_oid = "'"+row['oid']+"'"
      string_rid = "'"+row['rid']+"'"

      #Get list of menu items and quantities for order
      menu_items = []
      for row2 in c_orders:
        if row2['oid'] == row['oid']:
          menu_item = {'m_name': row2['m_name'], 'quantity': row2['quantity']}
          menu_items.append(menu_item)

      #Get all other info
      cursor2 = g.conn.execute("SELECT O.total_price, O.status, R.r_name, R.r_phone, D.d_name, D.d_phone FROM order_fulfilled_by_driver O, restaurant R, driver D WHERE O.oid={string_oid} AND O.did=D.did AND R.rid={string_rid}".format(string_oid=string_oid, string_rid=string_rid))
      c_orderdetails = []
      for result in cursor2:
        c_orderdetails.append(result)
      cursor2.close()

      order_info = {
        'oid': row['oid'],
        'r_name': c_orderdetails[0]['r_name'],
        'r_phone': c_orderdetails[0]['r_phone'],
        'total_price': c_orderdetails[0]['total_price'],
        'menu_items': menu_items,
        'status' : c_orderdetails[0]['status'],
        'd_name': c_orderdetails[0]['d_name'],
        'd_phone': c_orderdetails[0]['d_phone'],
      }
      if c_orderdetails[0]['status'] == 'Delivered':
        past.append(order_info)
      else:
        upcoming.append(order_info)

  return render_template('customer_orders.html', upcoming=upcoming, past=past)


@app.route('/<cid>/neworders')
def customer_new_orders(cid):
    string_cid = "'"+cid+"'"
    cursor = g.conn.execute("SELECT zip from lives_in where cid={string_cid}".format(string_cid=string_cid));
    zipcodes = []
    for results in cursor:
        zipcodes.append(results)
       # print('results: ' + results)
       # print(type(results))
        zipcode = int(results['zip'])
    
        forward = zipcode+1
        forward_2= zipcode+2
        zipcodes.append(str(forward))
        zipcodes.append(str(forward_2))
    rids = []
    cursor.close()
    cursor2 = g.conn.execute("SELECT rid from located_in where zip={string_zip} OR zip={string_forward_zip} OR zip= {string_forward_again}").format(string_zip="'" + zipcodes[0] + "'",string_forward_zip= "'" + zipcodes[1] + "'" ,string_forward_again= "'"+zipcodes[2]+"'")
    rids = []
    for results in cursor2:
        rids.append(results['rid'])
    cursor2.close()
    resturants = []
    for rid in rids:
        string_rid= "'"+rid+"'"
        cursor3 = g.conn.execute("SELECT * from restaurant where rid={string_rid}".format(string_rid=string_rid))
        for results in cursor3:
            resturants.append(results)
        cursor3.close()
    
    
    
    
    
    return render_template("customer_new_orders.html", resturants=resturants)





############################# DRIVER ####################################

@app.route('/driver')
def get_driver():
  return render_template('driver.html')

@app.route("/driver_login", methods=['POST'] )
def driver_login():
  name = request.form['l_name']
  email = request.form['l_email']
  name = "'"+name+"'"
  email = "'"+email+"'"

  cursor = g.conn.execute("SELECT did FROM driver WHERE d_email={email} AND d_name={name}".format(email=email, name=name))
  list_did = []
  for result in cursor:
      list_did.append(result[0])
  cursor.close()
  did = list_did[0]

  url = '/driver_main/' + did
  return redirect(url)

@app.route("/driver_signup")
def driver_signup():
  return render_template('driver_signup.html')

@app.route("/add_driver", methods=['POST'])
def add_driver():
  #This retrieves most recent driver id in the driver table, which lets us assign an id to a new driver
  cursor = g.conn.execute("SELECT did FROM driver ORDER BY did DESC LIMIT 1")
  last_did = []
  for result in cursor:
      last_did.append(result[0])
  cursor.close()

  name = request.form['s_name']
  email = request.form['s_email']
  phone = request.form['s_phone']
  did = 'D' + str(int(last_did[0][1:]) + 1)
  g.conn.execute('INSERT INTO driver VALUES (%s, %s, %s, %s)', did, email, phone, name)

  url = '/driver_main/' + did
  return redirect(url)

@app.route("/driver_main/<did>")
def driver_main(did):
  string_did = "'"+did+"'"
  #Get driver name from driver id
  cursor = g.conn.execute("SELECT d_name FROM driver WHERE did={string_did}".format(string_did=string_did))
  d_names = []
  for result in cursor:
    d_names.append(result[0])
  cursor.close()
  d_name = d_names[0]

  #Get all orders that are ready for pickup, or are on the way/delivered by this driver
  cursor2 = g.conn.execute("SELECT DISTINCT O.oid, O.status, C.c_name, C.c_phone, L1.number, L1.street, L1.apt, L1.zip, R.r_name, R.r_phone, L2.number AS r_number, L2.street AS r_street, L2.zip AS r_zip FROM places P, customer C, lives_in L1, restaurant R, located_in L2, order_fulfilled_by_driver O, order_has_menu_item M WHERE (O.status='Ready for Pickup' OR O.did={string_did}) AND P.oid=O.oid AND P.cid=C.cid AND P.cid=L1.cid AND P.oid=M.oid AND M.rid=R.rid AND R.rid=L2.rid".format(string_did=string_did))
  d_orderdetails = []
  for result in cursor2:
    d_orderdetails.append(result)
  cursor2.close()

  pending = []
  ready = []
  past = []
  for row in d_orderdetails:
    order_info = {
      'oid': row['oid'],
      'status': row['status'],
      'r_name': row['r_name'],
      'r_phone': row['r_phone'],
      'r_address': row['r_number'] + ' ' + row['r_street'] + ', New York, NY ' + row['r_zip'],
      'c_name': row['c_name'],
      'c_phone': row['c_phone'],
      'c_address': row['number'] + ' ' + row['street'] + ', Apt ' + row['apt'] + ', New York, NY ' + row['r_zip'],
      }
    if row['status'] == 'Delivery On the Way':
      pending.append(order_info)
    elif row['status'] == 'Ready for Pickup':
      ready.append(order_info)
    else:
      past.append(order_info)

  return render_template('driver_main.html', did = did, d_name = d_name, pending=pending, ready=ready, past=past)

@app.route("/<did>/<oid>/update_status_delivered", methods=['POST'] )
def update_status_delivered(did, oid):
  oid = "'"+oid+"'"
  g.conn.execute("UPDATE order_fulfilled_by_driver SET status = 'Delivered' WHERE status = 'Delivery On the Way' AND oid = {oid}".format(oid=oid))
  
  url = '/driver_main/' + did
  return redirect(url)

@app.route("/<did>/<oid>/update_status_otw", methods=['POST'] )
def update_status_otw(did, oid):
  oid = "'"+oid+"'"
  string_did = "'"+did+"'"
  g.conn.execute("UPDATE order_fulfilled_by_driver SET status = 'Delivery On the Way', did = {string_did} WHERE status = 'Ready for Pickup' AND oid = {oid}".format(string_did=string_did,oid=oid))
  
  url = '/driver_main/' + did
  return redirect(url)








############################# RESTAURANT ####################################

@app.route('/restaurant')
def get_restaurant():
  return render_template('restaurant.html')

@app.route("/restaurant_login", methods=['POST'] )
def restaurant_login():
  name = request.form['l_name']
  phone = request.form['l_phone']
  name = "'"+name+"'"
  phone = "'"+phone+"'"

  cursor = g.conn.execute("SELECT rid FROM restaurant WHERE r_name={name} AND r_phone={phone}".format(name=name, phone=phone))
  list_rid = []
  for result in cursor:
    list_rid.append(result[0])
  cursor.close()
  rid = list_rid[0]

  url = '/restaurant_main/' + rid
  return redirect(url)

@app.route("/restaurant_main/<rid>")
def restaurant_main(rid):
  string_rid = "'"+rid+"'"
  #Get restaurant name from rid
  cursor1 = g.conn.execute("SELECT r_name FROM restaurant WHERE rid={string_rid}".format(string_rid=string_rid))
  r_names = []
  for result in cursor1:
      r_names.append(result[0])
  cursor1.close()
  r_name = r_names[0]

  #Get all orders for rid
  cursor2 = g.conn.execute("SELECT oid, m_name, quantity FROM order_has_menu_item WHERE rid={string_rid}".format(string_rid=string_rid))
  r_orders = []
  for result in cursor2:
    r_orders.append(result)
  cursor2.close()
  
  unique_oid = [] #this will let us store just distinct oid's
  incoming = []
  pending = []
  past = []
  
  #iterate through r_orders to get info for all incoming, pending, and past orders
  for row in r_orders:
    if row['oid'] in unique_oid: #if we already have the info for this oid, move on to the next one
      continue
    else:
      unique_oid.append(row['oid'])
      string_oid = "'"+row['oid']+"'"

      #Get list of menu items and quantities for order
      menu_items = []
      for row2 in r_orders:
        if row2['oid'] == row['oid']:
          menu_item = {'m_name': row2['m_name'], 'quantity': row2['quantity']}
          menu_items.append(menu_item)

      #Get all other info
      cursor3 = g.conn.execute("SELECT O.total_price, O.status, C.c_name, D.d_name FROM order_fulfilled_by_driver O, places P, customer C, driver D WHERE O.oid={string_oid} AND O.did=D.did AND O.oid=P.oid AND P.cid=C.cid".format(string_oid=string_oid))
      r_orderdetails = []
      for result in cursor3:
        r_orderdetails.append(result)
      cursor3.close()

      order_info = {
        'oid': row['oid'],
        'c_name': r_orderdetails[0]['c_name'],
        'total_price': r_orderdetails[0]['total_price'],
        'menu_items': menu_items,
        'status' : r_orderdetails[0]['status'],
        'd_name': r_orderdetails[0]['d_name']
      }
      if r_orderdetails[0]['status'] == 'Processing':
        incoming.append(order_info)
      elif r_orderdetails[0]['status'] == 'Preparing Food' or r_orderdetails[0]['status'] == 'Ready for Pickup':
        pending.append(order_info)
      else:
        past.append(order_info)

  return render_template('restaurant_main.html', rid = rid, r_name = r_name, incoming = incoming, pending = pending, past = past)

@app.route("/<rid>/<oid>/update_status_preparing", methods=['POST'] )
def update_status_preparing(rid, oid):
  oid = "'"+oid+"'"
  g.conn.execute("UPDATE order_fulfilled_by_driver SET status = 'Preparing Food' WHERE status = 'Processing' AND oid = {oid}".format(oid=oid))
  
  url = '/restaurant_main/' + rid
  return redirect(url)

@app.route("/<rid>/<oid>/update_status_pickup", methods=['POST'] )
def update_status_pickup(rid, oid):
  oid = "'"+oid+"'"
  g.conn.execute("UPDATE order_fulfilled_by_driver SET status = 'Ready for Pickup' WHERE status = 'Preparing Food' AND oid = {oid}".format(oid=oid))
  
  url = '/restaurant_main/' + rid
  return redirect(url)







if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()
