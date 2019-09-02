from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm

app = Flask(__name__)

app.config['SECRET_KEY'] = '1f67b3678156205853ddc3ef59abafed'

posts = [
    {
        'author': 'James Ferguson',
        'title': 'This would have to be the most recent post',
        'content': 'Content for the first ever post',
        'date_posted': 'August 30, 2019'
    },
    {
        'author': 'James Ferguson',
        'title': 'This looks like a good place to put a first post',
        'content': 'Content for the second ever post',
        'date_posted': 'August 30, 2019'
    }
]


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts=posts) #post=posts is used as an argument here to pass the content of posts into the template so we can access the posts variable


@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'info')
        return redirect(url_for('home'))
    return render_template('register.html', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == "admin@myBlog.com" and form.password.data == 'password':
            flash(f'{form.email.data}, you have been logged in!', 'info')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)