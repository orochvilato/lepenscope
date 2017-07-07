/*
This demo visualises wine and cheese pairings.
*/

$(function(){

  var layoutPadding = 50;
  var aniDur = 500;
  var easing = 'linear';

  var cy;
  var cyreset;

  // get exported json from cytoscape desktop via ajax
  var graphP = $.ajax({
    //url: 'https://cdn.rawgit.com/maxkfranz/3d4d3c8eb808bd95bae7/raw', // wine-and-cheese.json
    url: 'reseau/reseau.json',
    type: 'GET',
    dataType: 'json'
  });

  // also get style via ajax
  var styleP = $.ajax({
    url: 'reseau/reseau.cycss', // wine-and-cheese-style.cycss
    type: 'GET',
    dataType: 'text'
  });
  
  var infoTemplate = Handlebars.compile([
    '<p class="ac-name">{{label}}</p>',
  ].join(''));
  
  // when both graph export json and style loaded, init cy
  Promise.all([ graphP, styleP ]).then(initCy);

  var allNodes = null;
  var allEles = null;
  var lastHighlighted = null;
  var lastUnhighlighted = null;

  function getFadePromise( ele, opacity ){
    return ele.animation({
      style: { 'opacity': opacity },
      duration: aniDur
    }).play().promise();
  };

  var restoreElesPositions = function( nhood ){
    return Promise.all( nhood.map(function( ele ){
      var p = ele.data('orgPos');

      return ele.animation({
        position: { x: p.x, y: p.y },
        duration: aniDur,
        easing: easing
      }).play().promise();
    }) );
  };

  function highlight( elt ){
    var oldNhood = lastHighlighted;

    if (elt.isNode()) {
      console.log('nodeselect');
      var nhood = lastHighlighted = elt.closedNeighborhood();
      var node = elt;
    } else {
      console.log('edgeselect');
      var nhood = lastHighlighted = elt.connectedNodes().union(elt);
      var node = nhood[0];
    }

    var others = lastUnhighlighted = cy.elements().not( nhood );

    var reset = function(){
      cy.batch(function(){
        others.addClass('hidden');
        nhood.removeClass('hidden');
        nhood.nodes().forEach(function(n) {
          n.data('label',n.data('orgLabel'));
        })

        allEles.removeClass('faded highlighted');

        nhood.addClass('highlighted');

        others.nodes().forEach(function(n){
          var p = n.data('orgPos');

          n.position({ x: p.x, y: p.y });
        });
      });

      return Promise.resolve().then(function(){
        if( isDirty() ){
          return fit();
        } else {
          return Promise.resolve();
        };
      }).then(function(){
        return Promise.delay( aniDur );
      });
    };

    var initLabels = function() {
      return Promise.resolve().then(function() {
        cy.batch(function() {
          nhood.nodes().forEach(function(n){
            var l = n.data('orgLabel');
            var edges = n.edgesWith(node);
            edges.edges().forEach(function(e){
              if (e.data('label') !== '') {
                n.data('label',l+' ('+e.data('label')+')');
              }
            })
          });
        });
      });

    }
    var runLayout = function(){
      var p = node.data('orgPos');

      var l = nhood.filter(':visible').makeLayout({
          name: 'cose-bilkent',
          nodeRepulsion: 10000,
          idealEdgeLength: 100,
          animate: true
      });


      var promise = cy.promiseOn('layoutstop');


      l.run();

      return promise;
    };

    var recenter = function() {
      var x_c = node.data('orgPos').x - node.position().x;
      var y_c = node.data('orgPos').y - node.position().y;
      return Promise.resolve().then(function() {
        cy.batch(function () {
          nhood.filter(':visible').nodes().forEach(function(n) {
              var _p = n.position()
              n.position({x:_p.x+x_c,y:_p.y+y_c});
          });
        });
      });
    }
    var fit = function(){
      return cy.animation({
        fit: {
          eles: nhood.filter(':visible'),
          padding: layoutPadding
        },
        easing: easing,
        duration: aniDur
      }).play().promise();
    };

    var showOthersFaded = function(){
      return Promise.delay( 250 ).then(function(){
        cy.batch(function(){
          others.removeClass('hidden').addClass('faded');
        });
      });
    };
    var loadFiche = function() {
      var ficheHTML = $.ajax({
          url: "fiches/"+node.data('shortId')+".html",
          context: $('#fiche')
      }).done(function(data) {
        $( this ).replaceWith(data);
        $('#fichetitle').goTo();
      });

      return Promise.all(ficheHTML);

    }
    var resizecy = function() {
      $('#cy').animate({
        marginTop: '20vh',
        height: '80vh'
      }, 'fast');
    }

    return Promise.resolve()
      .then( reset )
      .then( initLabels )
      .then( resizecy )
      .then( runLayout )
      .then( loadFiche )
      .then( fit )
      .then( showOthersFaded );


  }

  function isDirty(){
    return lastHighlighted != null;
  }

  function clear( opts ){
    if( !isDirty() ){ return Promise.resolve(); }

    opts = $.extend({

    }, opts);

    cy.stop();
    allNodes.stop();
    allEdges.stop();

    var nhood = lastHighlighted;
    var others = lastUnhighlighted;

    lastHighlighted = lastUnhighlighted = null;

    var hideOthers = function(){
      return Promise.delay( 125 ).then(function(){
        others.addClass('hidden');

        return Promise.delay( 125 );
      });
    };

    var showOthers = function(){
      cy.batch(function(){
        allEles.removeClass('hidden').removeClass('faded');
      });

      return Promise.delay( aniDur );
    };

    var restorePositions = function(){
      cy.batch(function(){
        others.nodes().forEach(function( n ){
          var p = n.data('orgPos');

          n.position({ x: p.x, y: p.y });
        });
      });

      return restoreElesPositions( nhood.nodes() );
    };

    var resetHighlight = function(){
      nhood.removeClass('highlighted');
      cy.batch(function() {
        allEles.nodes().forEach(function(n) {
          n.data('label',n.data('orgLabel'));
        });
      });
    };
    var scrolltop = function() {

      $('html, body').animate({
        scrollTop: 0,
      }, 'slow');
    }

    var resizecy = function() {
      $('#cy').animate({
        marginTop: '7.5vh',
        height: '92.5vh'
      }, 'fast');
    }

    return Promise.resolve()
      .then( resizecy )
      .then( resetHighlight )
      .then( hideOthers )
      .then( scrolltop )
      .then( restorePositions )
      .then( showOthers )
      .then( cyreset )
    ;
  }



  function initCy( then ){
    var loading = document.getElementById('loading');
    var expJson = then[0];
    var styleJson = then[1];
    var elements = expJson.elements;

    elements.nodes.forEach(function(n){
      var data = n.data;

      //data.NodeTypeFormatted = data.NodeType;

      //if( data.NodeTypeFormatted === 'RedWine' ){
      //  data.NodeTypeFormatted = 'Red Wine';
      //} else if( data.NodeTypeFormatted === 'WhiteWine' ){
      //  data.NodeTypeFormatted = 'White Wine';
      //}

      //n.data.orgPos = {
      //  x: n.position.x,
      //  y: n.position.y
      //};
    });

    //loading.classList.add('loaded');

    cy = window.cy = cytoscape({
      container: document.getElementById('cy'),
      layout: {
        ready: layoutready,
        name: 'cose-bilkent',
        nodeRepulsion: 10000,
        idealEdgeLength: 80,
        animate: false,
        fit: false
      },
      style: styleJson,
      elements: elements,
      motionBlur: true,
      selectionType: 'single',
      boxSelectionEnabled: false,
      zoom:1.5,
      minZoom:.5,
      maxZoom:3,
      wheelSensitivity:0.3,
      autoungrabify: true
    });
    allNodes = cy.nodes();
    allEdges = cy.edges();
    allEles = cy.elements();
    function layoutready(){
      allNodes.forEach(function( n ){
        var p = n.position();
        n.data('orgLabel',n.data('label'));
        n.data('orgPos',{
          x: p.x,
          y: p.y
        });
      });
      //var j = cy.$("#j");
      cy.center();

    };
    cy.on('free', 'node', function( e ){
      var n = e.cyTarget;
      var p = n.position();
      n.data('orgPos', {
        x: p.x,
        y: p.y
      });
    });

    cy.on('tap', function(){
      $('#search').blur();
    });

    cy.on('select unselect','edge,node',  _.debounce( function(e){
      var elt = cy.$(':selected');

      if( elt.nonempty() ){

        Promise.resolve().then(function(){
          return highlight( elt );
        });
      } else {
        clear();
      }

    }, 100 ) );



  }

  var lastSearch = '';

  $('#search').typeahead({
    minLength: 2,
    highlight: true,
  },
  {
    name: 'search-dataset',
    source: function( query, cb ){
      console.log(query);
      function matches( str, q ){
        str = (str || '').toLowerCase();
        q = (q || '').toLowerCase();

        return str.match( q );
      }

      var fields = ['label'];

      function anyFieldMatches( n ){
        for( var i = 0; i < fields.length; i++ ){
          var f = fields[i];

          if( matches( n.data(f), query ) ){
            return true;
          }
        }

        return false;
      }

      function getData(n){
        var data = n.data();

        return data;
      }

      function sortByName(n1, n2){
        if( n1.data('name') < n2.data('name') ){
          return -1;
        } else if( n1.data('name') > n2.data('name') ){
          return 1;
        }

        return 0;
      }

      var res = allNodes.stdFilter( anyFieldMatches ).sort( sortByName ).map( getData );

      cb( res );
    },
    templates: {
      suggestion: infoTemplate
    }
  }).on('typeahead:selected', function(e, entry, dataset){
    var n = cy.getElementById(entry.id);

    cy.batch(function(){
      allNodes.unselect();
      allEdges.unselect();

      n.select();
    });


  }).on('keydown keypress keyup change', _.debounce(function(e){
    var thisSearch = $('#search').val();

    if( thisSearch !== lastSearch ){
      $('.tt-dropdown-menu').scrollTop(0);

      lastSearch = thisSearch;
    }
  }, 50));

  cyreset = window.cyreset = function () {
    if( isDirty() ){
      clear();
    } else {
      allNodes.unselect();
      allEdges.unselect();



      cy.stop();

      cy.animation({
        fit: {
          eles: cy.elements(),
          padding: layoutPadding
        },
        duration: aniDur,
        easing: easing
      }).play();
    }
  }
  $('#reset').on('click', function(){
    cyreset();
  });

  $('#filters').on('click', 'input', function(){

    var personne = $('#personne').is(':checked');
    var mouvement = $('#mouvement').is(':checked');
    var autre = $('#autre').is(':checked');
    var Souverainiste = $('#Souverainiste').is(':checked');
    var Identitaire = $('#Identitaire').is(':checked');
    var Integriste = $('#Integriste').is(':checked');
    var Complotiste = $('#Complotiste').is(':checked');
    var Autres = $('#Autres').is(':checked');
    

    cy.batch(function(){

      allNodes.forEach(function( n ){
        var type = n.data('NodeType');

        n.removeClass('filtered');

        var filter = function(){
          n.addClass('filtered');
        };
        var cType = n.data('type');
        var cat = n.data('cat');
        if(
           (cType === 'personne' && !personne)
            || (cType === 'mouvement' && !mouvement)

            // categories
            || (cat === null && !autre)
            || (cat === 'Souverainiste' && !Souverainiste)
            || (cat === 'Identitaire' && !Identitaire)
            || (cat === 'Intégriste' && !Integriste)
            || (cat === 'Complotiste' && !Complotiste)
            || (cat === 'Autres' && !Autres)
            
          ){
            filter();
          }


      });

    });

  });



});