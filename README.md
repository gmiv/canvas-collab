# Canvas Collab

> Realtime Collaborative Whiteboard

This project is a super simple canvas painter in vanilla JavaScript with Socket.io over Node.js.

## Project Structure

- **public/**: Frontend files served to clients
  - **index.html**: Main HTML file
  - **css/**
    - **styles.css**: CSS styles
  - **js/**
    - **app.js**: Main client-side JavaScript
    - **canvas.js**: Canvas drawing functionalities
    - **socket.js**: Socket.io client-side logic
- **server/**
  - **server.js**: Node.js server with Socket.io
- **tests/**: Tests directory (unit, integration, system, performance, security)
- **package.json**: Project dependencies and scripts
- **.eslintrc.js**: Linting configuration
- **.gitignore**: Git ignore file
- **README.md**: Project documentation

## Setup Instructions

1. **Install Dependencies**

   ```bash
   npm install
   ```

2. **Run the Application**

   ```bash
   npm start
   ```

3. **Access the Application**

   Open your web browser and navigate to `http://localhost:3000`.

## Testing

- **Unit Tests**

  ```bash
  npm run test:unit
  ```

- **Integration Tests**

  ```bash
  npm run test:integration
  ```

- **System Tests**

  ```bash
  npm run test:system
  ```

- **Performance Tests**

  ```bash
  npm run test:performance
  ```

- **Security Tests**

  ```bash
  npm run test:security
  ```

- **Run All Tests**

  ```bash
  npm test
  ```

## License

This project is licensed under the MIT License.
