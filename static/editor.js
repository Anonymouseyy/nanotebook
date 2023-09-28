var Delta = Quill.import('delta');
var quill = new Quill('#editor', {
  modules: {
    toolbar: "#toolbar"
  },
  placeholder: 'Compose an epic...',
  theme: 'snow'
});