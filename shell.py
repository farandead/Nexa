import nexa
while True:
    text = input('nexa >')
    
    result,error = nexa.run("<stdin>",text)

    if error: print(error.as_string())
    else:
        print(result)

# First step is to create a Lexer that breaks down the inputs into token which have a type that may have values
