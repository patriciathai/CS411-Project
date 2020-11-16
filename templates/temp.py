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