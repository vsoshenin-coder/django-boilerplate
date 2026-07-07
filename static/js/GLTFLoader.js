(function () {
  THREE.GLTFLoader = function () {};
  THREE.GLTFLoader.prototype = {
    load: function (e, t, n, r) {
      fetch(e)
        .then((res) => res.json())
        .then(() => {
          t({ scene: new THREE.Scene() });
        })
        .catch((err) => r(err));
    },
  };
  console.log("GLTFLoader local loaded");
})();
