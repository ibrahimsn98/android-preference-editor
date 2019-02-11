def intInput(desc):
    while True:
        try:
            data = int(input(desc))
            break
        except Exception as e:
            print(e)
    return data
