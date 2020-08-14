import React from 'react';
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link
} from "react-router-dom";
import './App.css';
import HomePage from './pages/HomePage';
import 'bootstrap/dist/css/bootstrap.min.css';

console.log('INSIDE APP!');

function App() {
  return (
    <Router>
      <Switch>
        <Route path='/'>
          <HomePage />
        </Route>
      </Switch>
    </Router>
  );
}

export default App;
