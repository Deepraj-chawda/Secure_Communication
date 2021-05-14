# Secure Communications

 ### Secure communications system
    • Ali and Bianca want to communicate directly
    • First they must sign in to the system
    • The server knows their user ID and password
    • Once logged in, the server sends them the other’s IP address
    • They can now communicate directly
    

### Authentication phase
   ##### Authphase: Ali and Bianca each sign in
    1. User enters user ID 
    2. User enters passcode
    3. Application hashes the passcode
    4. Application encrypts user ID and passcode
    5. Application sends authentication request with user ID & passcode to server
    6. Server decrypts the user ID and passcode hash
    7. Server compares hashed passcode with stored hash passcode
    8. If they match
      • Server sends authentication grant message
      • Server stores user ID and user’s IP address
    9. Else, server sends authentication denied message


 ### Lookup phase: Ali --> Bianca

    1. Ali chooses “begin chat” and enters Bianca’s ID 
    2. Application sends lookup request with Bianca’s user ID to server
    3. Server looks up IP address for that user
    4. If user is found,
      • Server sends user IP address and encryption key
    5. Else, server sends Not-Found message
   
 
 ### Connect phase: Ali --> Bianca
    1. Ali’s application sends connect request to the application at Bianca’s IP address
    2. Bianca’s application sends lookup request with Ali’s user ID to server
    3. Server looks up Ali’s user data
    4.If user is found (Ali is logged in),
       • Server sends Ali’s IP address and encryption key
    5. Else, server sends Not-Found message
    6. Bianca’s application sends connect grant message to Ali’s application

#### Chat phase: Ali <--> Bianca
    1. Ali and Bianca type lines 
    2. Each application encrypts the line just entered
    3. Each application sends the encrypted message to the other application
    4. Each application decrypts messages received and displays them to the screen

### Hangupphase: Ali | Bianca
    1. Either Ali or Bianca types a CTRL-C KeyboardInterrupt
    2. Application sends a disconnect request to the other application
    3. Each application displays “Hang up” to the user(a disconnect request always results in the end of the chat session)


 ## State machines to handle complexity
  #### Client Application is in one of several possible states
    • Idle –waiting for user to log in
    • Logged in –waiting for user to request a chat or for connect request
    • Requesting chat –User made a request, waiting for other side
    • Chatting –sending and receiving messages


# Communications protocol
    The chat session must start with several phases to log in to the system, request user information and
    request a chat connection before any messages can be exchanged. The chat client goes through several 
    states during the phases of the connection. Information exchange between server and client is done with 
    JSON formatted messages. Each message is a sequence of name:value pairs. Message types are identified with
    the msgtype key present in all messages.


## Authentication phase
    Each client sends an Authentication Request to the server. The authentication request includes 
    the user ID and the hashed passcode. The server looks up the user ID and compares the hashed passcode
    to the hashed passcode it has stored. If the hashed passcodes match, the server returns an Authentication
    Reply message and also stores the current IP address of the user who has just authenticated.
    
    The client sends an Authentication Request message to the server (Listing 1).
      • msgtype: “AUTHREQ”
      • userid: string as entered by the user making the request;
      • passcode: the user’s passcode entered by the user on the keypad, then salted and hashed (see passcode hashing section).
    
    Listing 1: Authentication Request message example
          {
          "msgtype": "AUTHREQ", "userid": "ali",
          "passcode": "0023dc6bc244d474d2237ab53d256430b14eabe6db"
          }
          
     
     The server sends the Authentication Reply message to the client telling the client if the user is authenticated or not. 
     The value of the status key is either “GRANTED” if successful (Listing 2), or “REFUSED” otherwise (Listing 3).
           
           • msgtype: “AUTHREPLY”
           • userid: string as entered by the user making the request;
           • status: “GRANTED” if the credentials were accepted, “REFUSED” otherwise.


      Listing 1: Authentication Request message example
          {
          "msgtype": "AUTHREQ", "userid": "ali",
          "passcode": "0023dc6bc244d474d2237ab53d256430b14eabe6db"
          }
      
      
      Listing 2: Authentication Reply message example – successful authentication
          {
          "msgtype": "AUTHREPLY", "status": "GRANTED"
          }
          
     
      Listing 3: Authentication Grant message example – authentication refused
            {
            "msgtype": "AUTHREPLY", "status": "REFUSED"
            }



 ## Lookup phase
      
      The initiating client sends a Lookup Request to the server. The request includes the user ID of the initiator 
      and the user ID of the person the initiator wishes to contact. The server replies with a Lookup Reply message 
      giving information about the person, or no information if that person is not logged in. As a precaution against 
      requests by users not logged in, the server also replies with no information if the user making the request is not 
      logged in. The server replies with a Lookup Reply message. The reply includes the user ID of the person the initiator
      wishes to contact, the IP address of her/his client and (optional) the encryption key to be used when communicating 
      with that person.
      
    
      The client sends the Lookup Request message to the server (Listing 4).
          • msgtype: “LOOKUPREQ”;
          • userid: string as entered by the user making the request;
          • lookup: the user ID of the person that the user is calling.
          
          
      Listing 4: Lookup Request message example

              {
              "msgtype": "LOOKUPREQ", "userid": "ali",
              "lookup": "bianca"
              }
              
              
       The server sends the Lookup Reply message to the client, with “status”:“SUCCESS” and information if found (Listing 5),
       or “status”:“NOTFOUND” and empty information fields otherwise (Listing 6).
       
              • msgtype: “LOOKUPREPLY”;
              • status: “SUCCESS” if the user ID is logged in, “NOTFOUND” otherwise
              • answer: the user ID of the person that the user is calling;
              • address: the IP address of the remote user;
              • encryptionkey: the encryption key as a string.
              
              
              Listing 5: Lookup Reply message example – User found, information returned
                          {
                          "msgtype": "LOOKUPREPLY",
                          "status": "SUCCESS",
                          "answer": "bianca", "address": "192.168.1.23",
                          "encryptionkey": "1234"
                          }
                          
                          
              Listing 6: Lookup Reply message example – User not found
                          {
                          "msgtype": "LOOKUPREPLY", "status": "NOTFOUND", "answer": "",
                          "location": "", "encryptionkey": ""
                          }
                          
                          
                          
  ## Connection phase
        
        The initiating terminal sends a Connection Request to the destination terminal. The request includes the user ID
        of the initiator. The destination terminal performs a Lookup Request of its own to the server and, if the address
        of the initiating user’s terminal matches the one registered with the server, the destination terminal replies with 
        a Connect Reply “accepted” message to go ahead with the chat session, otherwise it sends a Connect Reply “refused” message.

      The initiator sends the Connect Request message to the destination terminal (Listing 7).
          • msgtype: “CONNECTREQ”;
          • initiator: the user ID of the person making the request.
          
          
     Listing 7: Connect Request message example – Ali requests connection to Bianca
              {
              "msgtype": "CONNECTREQ", "initiator": "ali"
              }
              
              
    
    The destination sends the Connect Reply message “status”:“ACCEPTED” to the initiator terminal (Listing 8), or 
     “status”:“REFUSED” otherwise (Listing 9).
        
          • msgtype: “CONNECTREPLY”;
          • answer: “ACCEPTED” or “REFUSED”.
          
          
       
    Listing 8: Connect Reply message example – Connection request accepted by destination
                {
                "msgtype": "CONNECTREPLY",
                "status": "ACCEPTED"
                }
    
    
    Listing 9: Connect Reply message example – Connection request refused
                {
                "msgtype": "CONNECTREPLY",
                "status": "REFUSED"
                }
          
        

 ## Chat phase

    No special messaging format is required in the chat phase. The two-way connection is established between terminals 
    and the main loop can simply read from the open connection as if it was a stream of bytes. Each client can “catch” 
    the CTRL-C KeyboardInterrupt to end the chat at any time. No special protocol is needed to end a session.
    
    
