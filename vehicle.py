from flask import Flask, render_template,request,redirect

app = Flask(__name__)

cars = [
    {"nickname": "First Car", "model": "EMAS 5", "year": 2022},
    {"nickname": "Second Car", "model": "EMAS 7", "year": 2026}
]


@app.route("/")
def home():
    return render_template("Home.html")

@app.route("/vehicle")
def vehicle():
    image_map = {
        "EMAS 5": "/static/image/emas5.jpg",
        "EMAS 7": "/static/image/emas7.jpg",
        "EMAS PHEV": "/static/image/emasphev.jpg"
    }

    for car in cars:
        car["image"] = image_map[car["model"]]

    return render_template("vehicle.html", cars=cars,car_count=len(cars))

@app.route("/add_car",methods=["POST"])
def add_car():
    nickname = request.form["nickname"]
    year = request.form["year"]
    model = request.form["model"]

    new_car = {
        "nickname":nickname,
        "year":year,
        "model":model
    }

    cars.append(new_car)
    
    return redirect("/vehicle")

@app.route("/location")
def location():
    return render_template("location.html")

@app.route("/upgrade")
def upgrade():
    return render_template("upgrade.html")

if __name__ == "__main__":
    app.run(debug=True)