from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///leads.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Model
class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    company = db.Column(db.String(100))
    linkedin = db.Column(db.String(200))
    status = db.Column(db.String(50))
    notes = db.Column(db.String(300))
    meeting_date = db.Column(db.Date)
    meeting_time = db.Column(db.Time)

# Create DB
with app.app_context():
    db.create_all()

# Home - View Leads
@app.route('/')
def index():
    search = request.args.get('q')

    if search:
        leads = Lead.query.filter(
            (Lead.name.contains(search)) | (Lead.company.contains(search))
        ).all()
    else:
        leads = Lead.query.all()

    # Dashboard stats
    total = len(leads)
    replied = len([l for l in leads if l.status == "Replied"])
    messaged = len([l for l in leads if l.status == "Messaged"])
    closed = len([l for l in leads if l.status == "Closed"])

    # Format time for display (AM/PM)
    for lead in leads:
        if lead.meeting_time:
            lead.formatted_time = lead.meeting_time.strftime('%I:%M %p')
        else:
            lead.formatted_time = None

    return render_template(
        'index.html',
        leads=leads,
        total=total,
        replied=replied,
        messaged=messaged,
        closed=closed,
        current_date=date.today()
    )

# Add Lead
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        date_input = request.form.get('meeting_date')
        time_input = request.form.get('meeting_time')

        new_lead = Lead(
            name=request.form['name'],
            company=request.form['company'],
            linkedin=request.form['linkedin'],
            status=request.form['status'],
            notes=request.form['notes'],
            meeting_date=datetime.strptime(date_input, '%Y-%m-%d').date() if date_input else None,
            meeting_time=datetime.strptime(time_input, '%H:%M').time() if time_input else None
        )

        db.session.add(new_lead)
        db.session.commit()
        return redirect('/')

    return render_template('add.html')

# Update Lead
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    lead = Lead.query.get_or_404(id)

    if request.method == 'POST':
        date_input = request.form.get('meeting_date')
        time_input = request.form.get('meeting_time')

        lead.name = request.form['name']
        lead.company = request.form['company']
        lead.linkedin = request.form['linkedin']
        lead.status = request.form['status']
        lead.notes = request.form['notes']
        lead.meeting_date = datetime.strptime(date_input, '%Y-%m-%d').date() if date_input else None
        lead.meeting_time = datetime.strptime(time_input, '%H:%M').time() if time_input else None

        db.session.commit()
        return redirect('/')

    return render_template('update.html', lead=lead)

# Delete Lead
@app.route('/delete/<int:id>')
def delete(id):
    lead = Lead.query.get_or_404(id)
    db.session.delete(lead)
    db.session.commit()
    return redirect('/')
        
if __name__ == '__main__':
    app.run(debug=True)