class Error_Handler:
    EmptyValueError = f"""
        <script>
            alert('Request Error. Empty entry detected');
            window.location.href = '/';  // Redirect to the home page or any other desired page
        </script>
    """ 
    zipCodeError = f"""
        <script>
            alert('Request Error. Please enter a valid zip code');
            window.location.href = '/';  // Redirect to the home page or any other desired page
        </script>
    """ 

    inputSuccess = f"""
        <script>
            alert('Request submitted!');
            window.location.href = '/';  // Redirect to the home page or any other desired page
        </script>
    """ #return a script that will display information to the user