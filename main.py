from flask import Flask, render_template, request, g, session, redirect
import BF_Machine
import re
app = Flask(__name__)
app.secret_key = 'FUCK YOU SHOULD NOT BE SEEING THIS'

@app.route('/BFD', methods=['GET', 'POST'])
def BFD():
	if request.method == "GET":
		session['pc'] = -1
		return render_template("BFDIN.html")
	else:
		noPost = False
		if session['pc'] == -1:
			#first time, grab code
			session['code'] = request.form['code']
			try:
				session['code'][0]
			except:
				return redirect("/BFD")
			session['pc'] = 0
			session['scroll'] = 0
			noPost = True
		machine = BF_Machine.Machine(80)
		success = machine.loadCode(session['code'])
		if not success: 
			return redirect("/BFD")
		#get back to old state
		machine.runFor(session['pc'])
		if noPost == False:
			if request.form["post"] == "step+":
				machine.step()
			elif request.form["post"] == "step-":
				reset = session['pc'] - 1
				machine = getDefaultMachine()
				machine.runFor(reset)
			elif request.form["post"] == "skip":
				machine.skipLoop()
			elif request.form["post"] == "run":
				machine.run()
			elif request.form["post"] == "next":
				machine.nextLoop(True)
			session['pc'] = machine.cycles
			session['scroll'] = request.form['scroll']

		return render_template('BFD.html', code=machine.codeToHTML(), console=machine.consoleToHTML(), memory=machine.memoryToHTML(), scroll=session['scroll'])


if __name__ == '__main__':
    app.run(debug=True)