fn main() raises:
    let x = PythonObject(10)
    let y = PythonObject(20)

    let int_x: Int = y.to_float64().to_int()
    
    print(int_x)