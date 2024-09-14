import { useState } from 'react';
import './App.css';
const uuid = require('uuid');

function App() {

  const [Image , setImage] = useState('');
  const [UploadResultMessage , setUploadResultMessage] = useState('Please Enter image to authenticate');
  const [imgName , setimgName] = useState('placeholder.jpg');
  const [isAuth , setAuth] = useState(false);

  function sendImage(e) {
    e.preventDefault();
    setimgName(Image.name);
    const visitorImageName = uuid.v4();
    
    // Upload image to S3
    fetch(`https://q2qrd3qjm6.execute-api.ap-northeast-1.amazonaws.com/dev/visitor-pictures-dsa/${visitorImageName}.jpeg` , {
      method: 'PUT',
      headers: {
        'Content-Type':'image/jpeg'
      },
      body: Image
    }).then(async () => {
      const response = await authenticate(visitorImageName);
      
      // Log the response from the backend to verify its structure
      console.log("Response from backend:", response);

      // Check if authentication was successful
      if(response.Message === 'Success'){
        setAuth(true);
        setUploadResultMessage(`Hi ${response['firstName']} ${response['lastName']} , Welcome to work `);
      }
      else{
        setAuth(false);
        setUploadResultMessage('Authentication failed: This person is not an employee of this office');
      }
    }).catch(error => {
      setAuth(false);
      setUploadResultMessage('There was an error in the authentication process. Please try again.');
      console.error('Error during authentication:', error);
    });
  }

  async function authenticate(visitorImageName){
    const requestURL = 'https://q2qrd3qjm6.execute-api.ap-northeast-1.amazonaws.com/dev/employee?' + new URLSearchParams({
      objectKey: `${visitorImageName}.jpeg`
    });
    
    // Fetch the authentication result
    return await fetch(requestURL, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    }).then(response => response.json())
      .then((data) => {
        return data;
      }).catch(error => console.log('Error fetching authentication data:', error));
  }

  return (
    <div className="App">
      <h2>Facial Recognition System</h2>
      <form onSubmit={sendImage}>
        <input type='file' name='image' onChange={e => setImage(e.target.files[0])}/>
        <button type='submit'>Authenticate</button>
      </form>
      <div className={isAuth ? 'success' : 'failure'}>{UploadResultMessage}</div>
      <img src={require(`./visitors/${imgName}`)} alt='Visitor' height={250} width={250}/>
    </div>
  );
}

export default App;
