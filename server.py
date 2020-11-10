
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

engine.execute("""CREATE TABLE IF NOT EXISTS customer_temp (
  cid		varchar(10),
	c_email	varchar(30),
	c_phone	char(10),
	c_name	varchar(20),
);""")

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

@app.route('/driver')
def get_driver():
  return render_template('driver.html')

@app.route('/restaurant')
def get_restaurant():
  return render_template('restaurant.html')

#This retrieves most recent customer id in the customer table, which lets us assign an id to a new customer
cursor = g.conn.execute("SELECT cid FROM customer ORDER BY cid DESC LIMIT 1")
last_cid = cursor[0][0]
cursor.close()

@app.route("/customer_signup")
def customer_signup():
  name = request.form['s_name']
  email = request.form['s_email']
  phone = request.form['s_phone']
  cid = str(int(last_cid) + 1).zfill(5)

  g.conn.execute('INSERT INTO customer_temp VALUES (%s, %s, %s, %s)', cid, email, phone, name)
  return render_template('customer_signup.html', ) #this will redirect to page where user can provide an address and payment method, so we need to store the cid in the url

@app.route(
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
