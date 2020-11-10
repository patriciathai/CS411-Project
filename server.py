
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

@app.route('/customer')
def get_customer():
  return render_template('customer.html')

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
  cursor = g.conn.execute("SELECT c_name FROM customer WHERE cid={cid}".format(cid=cid))
  c_names = []
  for result in cursor:
    c_names.append(result[0])  # can also be accessed using result[0]
  cursor.close()
  c_name = c_names[0]
  
  return render_template('customer_main.html', cid = cid, c_name = c_name)

@app.route('/driver')
def get_driver():
  return render_template('driver.html')

@app.route('/restaurant')
def get_restaurant():
  return render_template('restaurant.html')

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
