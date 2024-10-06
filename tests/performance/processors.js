// processors.js
module.exports = {
  connectSocket: function (context, events, done) {
    context.vars.socket = require('socket.io-client')(context.config.target);
    context.vars.socket.on('connect', () => {
      // Emit submitName event
      context.vars.socket.emit('submitName', { name: `User_${Math.floor(Math.random() * 1000)}` });
      done();
    });
  },
  sendDrawingData: function (context, events, done) {
    const socket = context.vars.socket;
    const drawingData = {
      x0: Math.random() * 500,
      y0: Math.random() * 500,
      x1: Math.random() * 500,
      y1: Math.random() * 500,
      thickness: Math.floor(Math.random() * 10) + 1,
      userId: `User_${Math.floor(Math.random() * 1000)}`,
    };
    socket.emit('drawing', drawingData);
    done();
  },
};