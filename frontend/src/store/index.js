import { createStore } from 'vuex';
import auth from './modules/auth';
import notes from './modules/notes';

export default createStore({
  modules: {
    auth,
    notes
 }
});