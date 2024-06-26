import axios from 'axios'

const instance = axios.create({
  baseURL: 'http://ionos.local/api/v1/',
});

export default instance;
