/**
 * Sondage identité Teatower — backend Google Apps Script
 * --------------------------------------------------------
 * - doPost  : reçoit une réponse du formulaire et l'ajoute au Google Sheet.
 * - doGet   : affiche le DASHBOARD d'analyse (moyennes, distributions, verbatims).
 *
 * Déploiement : voir README_DEPLOIEMENT.md
 *   1. Crée un Google Sheet, menu Extensions > Apps Script, colle ce code.
 *   2. Déployer > Nouveau déploiement > Application Web
 *      - Exécuter en tant que : MOI
 *      - Qui a accès : TOUTE PERSONNE
 *   3. Copie l'URL /exec -> donne-la à Nira pour le formulaire.
 *   4. Le récap : <URL>/exec?key=teatower2026
 */

// ⚙️  Change ce mot de passe (sert à protéger l'accès au dashboard)
var SECRET = 'teatower2026';
var SHEET_NAME = 'Réponses';

// Champs dans l'ordre des colonnes (ts = horodatage, ajouté auto)
var FIELDS = ['ts','name','role','three_words','defining_points','mission','fierte',
  'vs_concurrents','atout','positionnement','client_type','qualite','gamme_coherence',
  'produit_phare','visuel','couleurs','nom','packaging','changer_une_chose','valeurs',
  'dans_3_ans','mot_fin',
  'force','manque','boutiques_importance','magasins','export_priorite','export_marches'];

var HEADERS = ['Horodatage','Prénom','Rôle','3 mots','★ Points qui définissent TT','Mission',
  'Fierté','Pourquoi TT vs concurrence','Principal atout','Positionnement (1-5)','Client type',
  'Qualité (1-5)','Cohérence gamme (1-5)','Produit phare','Identité visuelle (1-5)',
  'Couleurs collent ?','Nom Teatower (1-5)','Packaging (1-5)','Une chose à changer',
  'Valeurs','Dans 3 ans connue pour','Mot de la fin',
  '★ Plus grande force','★ Ce qui manque','Importance boutiques (1-5)',
  'Avenir boutiques/retail','Export prioritaire (1-5)','Marchés export visés'];

// Métadonnées pour le dashboard
var META = [
  {f:'name', label:'Prénom', type:'text'},
  {f:'role', label:'Rôle / département', type:'choice'},
  {f:'three_words', label:'Teatower en 3 mots', type:'text'},
  {f:'defining_points', label:'★ Les 3-5 points qui définissent Teatower', type:'long', star:true},
  {f:'mission', label:'La mission de Teatower', type:'long'},
  {f:'fierte', label:'Fierté de travailler chez Teatower', type:'long'},
  {f:'vs_concurrents', label:'Pourquoi TT plutôt que Palais des Thés / Kusmi / Dammann', type:'long'},
  {f:'atout', label:'Principal atout vs concurrence', type:'choice'},
  {f:'positionnement', label:'Positionnement marché (1 accessible → 5 premium)', type:'scale'},
  {f:'client_type', label:'Client type', type:'long'},
  {f:'force', label:'★ La plus grande force de Teatower', type:'long', star:true},
  {f:'manque', label:'★ Ce qui manque le plus à Teatower', type:'long', star:true},
  {f:'qualite', label:'Qualité produit (1 faible → 5 excellente)', type:'scale'},
  {f:'gamme_coherence', label:'Cohérence de la gamme (1 dispersée → 5 cohérente)', type:'scale'},
  {f:'produit_phare', label:'Produit qui incarne Teatower', type:'text'},
  {f:'visuel', label:'Identité visuelle (1 → 5)', type:'scale'},
  {f:'couleurs', label:'Les couleurs collent à la marque', type:'choice'},
  {f:'nom', label:'Le nom « Teatower » (1 mauvais → 5 excellent)', type:'scale'},
  {f:'packaging', label:'Packagings donnent envie (1 → 5)', type:'scale'},
  {f:'changer_une_chose', label:'Une chose à changer dans l\'image', type:'long'},
  {f:'boutiques_importance', label:'Importance des boutiques Namur/Liège/Waterloo (1 accessoires → 5 essentielles)', type:'scale'},
  {f:'magasins', label:'Avenir des boutiques / retail physique', type:'long'},
  {f:'export_priorite', label:'Développement export / international (1 → 5)', type:'scale'},
  {f:'export_marches', label:'Marchés export prioritaires', type:'long'},
  {f:'valeurs', label:'Valeurs à incarner', type:'multi'},
  {f:'dans_3_ans', label:'Dans 3 ans, connue pour…', type:'long'},
  {f:'mot_fin', label:'Mot de la fin', type:'long'}
];

function getSheet_(){
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(SHEET_NAME);
  if(!sh){ sh = ss.insertSheet(SHEET_NAME); }
  if(sh.getLastRow() === 0){
    sh.appendRow(HEADERS);
    sh.getRange(1,1,1,HEADERS.length).setFontWeight('bold').setBackground('#2d6a4f').setFontColor('#ffffff');
    sh.setFrozenRows(1);
  }
  return sh;
}

function doPost(e){
  try{
    var data = JSON.parse(e.postData.contents);
    var sh = getSheet_();
    var row = FIELDS.map(function(f){
      if(f === 'ts') return new Date();
      var v = data[f];
      if(Array.isArray(v)) return v.join(' | ');
      return (v === undefined || v === null) ? '' : v;
    });
    sh.appendRow(row);
    return ContentService.createTextOutput(JSON.stringify({ok:true}))
      .setMimeType(ContentService.MimeType.JSON);
  }catch(err){
    return ContentService.createTextOutput(JSON.stringify({ok:false, error:String(err)}))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet(e){
  var key = (e && e.parameter && e.parameter.key) ? e.parameter.key : '';
  if(key !== SECRET){
    return HtmlService.createHtmlOutput(
      '<div style="font-family:Segoe UI,sans-serif;text-align:center;padding:60px">' +
      '<h2>🔒 Accès réservé</h2><p>Ajoute <code>?key=TON_CODE</code> à la fin de l\'URL.</p></div>'
    ).setTitle('Récap Teatower');
  }
  return HtmlService.createHtmlOutput(buildDashboard_()).setTitle('Récap Sondage Teatower');
}

function colIndex_(f){ return FIELDS.indexOf(f); }
function esc_(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

function buildDashboard_(){
  var sh = getSheet_();
  var values = sh.getDataRange().getValues();
  var rows = values.slice(1); // sans l'en-tête
  var n = rows.length;

  var css = '<style>'+
    'body{font-family:Segoe UI,system-ui,sans-serif;background:#f4f7f4;color:#1b2a25;margin:0;padding:0}'+
    '.wrap{max-width:860px;margin:0 auto;padding:1rem}'+
    'h1{color:#2d6a4f;margin:1rem 0 .2rem}'+
    '.sub{color:#5c6b64;margin-bottom:1.2rem}'+
    '.kpi{display:inline-block;background:#2d6a4f;color:#fff;border-radius:12px;padding:.7rem 1.2rem;font-weight:700;margin-bottom:1rem}'+
    '.card{background:#fff;border:1px solid #e2eae4;border-radius:12px;padding:1rem 1.2rem;margin-bottom:1rem;box-shadow:0 2px 8px rgba(0,0,0,.05)}'+
    '.card.star{border-left:5px solid #2d6a4f;background:#f3fbf5}'+
    '.qlabel{font-weight:700;margin-bottom:.7rem;font-size:1rem}'+
    '.avg{font-size:2rem;font-weight:800;color:#2d6a4f}'+
    '.avg small{font-size:.95rem;color:#5c6b64;font-weight:500}'+
    '.bar{background:#e2eae4;border-radius:6px;height:22px;overflow:hidden;margin:.25rem 0}'+
    '.bar>span{display:block;height:100%;background:#40916c;color:#fff;font-size:.75rem;line-height:22px;padding-left:6px;white-space:nowrap}'+
    '.dist{display:grid;grid-template-columns:130px 1fr 36px;gap:.4rem;align-items:center;font-size:.85rem;margin:.2rem 0}'+
    '.verb{border-left:3px solid #d8f3dc;padding:.45rem .7rem;margin:.4rem 0;background:#fcfdfc;border-radius:0 6px 6px 0;font-size:.92rem}'+
    '.verb .who{color:#2d6a4f;font-weight:700;font-size:.8rem}'+
    '.tag{display:inline-block;background:#d8f3dc;color:#2d6a4f;border-radius:14px;padding:.2rem .6rem;margin:.15rem;font-size:.82rem;font-weight:600}'+
    '.muted{color:#9aa5a0;font-style:italic}'+
    '.print{position:fixed;top:14px;right:14px;background:#2d6a4f;color:#fff;border:none;border-radius:8px;padding:.5rem .9rem;cursor:pointer;font-weight:600}'+
    '@media print{.print{display:none}}'+
    '</style>';

  var html = css + '<button class="print" onclick="window.print()">🖨️ Imprimer / PDF</button><div class="wrap">';
  html += '<h1>🍵 Récap Sondage — Teatower, c\'est quoi&nbsp;?</h1>';
  html += '<div class="sub">Synthèse des réponses de l\'équipe pour le CA.</div>';
  html += '<div class="kpi">'+ n +' réponse'+(n>1?'s':'')+' reçue'+(n>1?'s':'')+'</div>';

  if(n === 0){
    html += '<div class="card"><p class="muted">Aucune réponse pour l\'instant. Reviens ici une fois le formulaire partagé.</p></div></div>';
    return html;
  }

  META.forEach(function(m){
    var ci = colIndex_(m.f);
    html += (m.star ? '<div class="card star">' : '<div class="card">');
    html += '<div class="qlabel">'+ esc_(m.label) +'</div>';

    if(m.type === 'scale'){
      var nums = [], counts = {1:0,2:0,3:0,4:0,5:0};
      rows.forEach(function(r){
        var v = parseInt(r[ci],10);
        if(v>=1 && v<=5){ nums.push(v); counts[v]++; }
      });
      if(nums.length){
        var avg = nums.reduce(function(a,b){return a+b;},0)/nums.length;
        html += '<div class="avg">'+ avg.toFixed(1) +' <small>/ 5 · moyenne sur '+nums.length+' réponse'+(nums.length>1?'s':'')+'</small></div>';
        for(var s=5;s>=1;s--){
          var pct = nums.length ? Math.round(counts[s]/nums.length*100) : 0;
          html += '<div class="dist"><span>Note '+s+'</span><div class="bar"><span style="width:'+Math.max(pct,2)+'%">'+(pct>8?pct+'%':'')+'</span></div><span>'+counts[s]+'</span></div>';
        }
      } else { html += '<p class="muted">Pas de réponse.</p>'; }

    } else if(m.type === 'choice' || m.type === 'multi'){
      var dist = {}, total = 0;
      rows.forEach(function(r){
        var raw = String(r[ci]||'').trim();
        if(!raw) return;
        var parts = (m.type==='multi') ? raw.split('|').map(function(x){return x.trim();}) : [raw];
        parts.forEach(function(p){ if(p){ dist[p]=(dist[p]||0)+1; total++; } });
      });
      var keys = Object.keys(dist).sort(function(a,b){return dist[b]-dist[a];});
      if(keys.length){
        if(m.type==='multi'){
          keys.forEach(function(k){ html += '<span class="tag">'+esc_(k)+' · '+dist[k]+'</span>'; });
        } else {
          keys.forEach(function(k){
            var pct = Math.round(dist[k]/n*100);
            html += '<div class="dist"><span>'+esc_(k)+'</span><div class="bar"><span style="width:'+Math.max(pct,2)+'%">'+(pct>8?pct+'%':'')+'</span></div><span>'+dist[k]+'</span></div>';
          });
        }
      } else { html += '<p class="muted">Pas de réponse.</p>'; }

    } else { // text / long  -> verbatims
      var any = false;
      rows.forEach(function(r){
        var v = String(r[ci]||'').trim();
        if(!v) return;
        any = true;
        var who = String(r[colIndex_('name')]||'Anonyme').trim() || 'Anonyme';
        var role = String(r[colIndex_('role')]||'').trim();
        html += '<div class="verb"><div class="who">'+esc_(who)+(role?' · '+esc_(role):'')+'</div>'+ esc_(v).replace(/\n/g,'<br>') +'</div>';
      });
      if(!any) html += '<p class="muted">Pas de réponse.</p>';
    }
    html += '</div>';
  });

  html += '</div>';
  return html;
}
