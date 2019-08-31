from flask import Flask, render_template, url_for

app = Flask(__name__)

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


if __name__ == '__main__':
    app.run(debug=True)