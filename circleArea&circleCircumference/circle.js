function circleArea(r) {
    const pi = 3.14
    const result = (pi * r**2)
    console.log(result)
}

function circleCircumference (r){
    const pi = 3.14
    const result = (2*pi*r)
    console.log(result)
}

module.exports={
    circleArea,
    circleCircumference
}