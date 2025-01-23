(window.webpackJsonp=window.webpackJsonp||[]).push([[0],{13:function(o,e,t){"use strict";t.r(e);var r=t(0),n=t.n(r),a=t(3),l=t.n(a),s=t(1);var c=function(){const[o,e]=Object(r.useState)({gameId:"",board:Array(8).fill(null).map(()=>Array(8).fill("")),currentPlayer:"red",status:"active",createdAt:"",updatedAt:""}),[t,a]=Object(r.useState)(null),[l,c]=Object(r.useState)([]),i="https://w9cqnnyhbi.execute-api.us-east-1.amazonaws.com/prod",d=e=>{let t=0;for(let r=0;r<8;r++)for(let n=0;n<8;n++){const a=o.board[r][n];a&&a.toLowerCase()===e&&t++}return t},u=(e,t)=>{const r=o.board[e][t];if(console.log("Calculating moves for piece:",{row:e,col:t,piece:r,isKing:r===r.toUpperCase(),isBlackSquare:(e+t)%2===0}),!r)return[];const n=r===r.toUpperCase(),a=[],l=[];"r"===r.toLowerCase()?l.push(-1):"b"===r.toLowerCase()&&l.push(1),n&&(l.includes(-1)||l.push(-1),l.includes(1)||l.push(1)),console.log("Movement directions:",l);const s=[];for(const i of l)for(const n of[-1,1]){var c;const a=e+i,l=t+n,d=e+2*i,u=t+2*n;if(console.log("Checking jump:",{from:{row:e,col:t},over:{row:a,col:l,piece:null===(c=o.board[a])||void 0===c?void 0:c[l]},to:{row:d,col:u},isBlackSquare:(d+u)%2===0}),d<0||d>7||u<0||u>7){console.log("Jump out of bounds");continue}const p=o.board[a][l];if(!p){console.log("No piece to jump over");continue}if(o.board[d][u]){console.log("Landing square occupied");continue}const m="r"===r.toLowerCase()&&"b"===p.toLowerCase()||"b"===r.toLowerCase()&&"r"===p.toLowerCase();console.log("Jump validation:",{isOpponentPiece:m,isBlackSquare:(d+u)%2===0}),m&&(d+u)%2===0&&(s.push({row:d,col:u}),console.log("Valid jump found:",{row:d,col:u}))}if(s.length>0)return console.log("Mandatory jumps found:",s),s;for(const i of l)for(const r of[-1,1]){const n=e+i,l=t+r;if(console.log("Checking regular move:",{from:{row:e,col:t},to:{row:n,col:l},isBlackSquare:(n+l)%2===0}),n<0||n>7||l<0||l>7){console.log("Move out of bounds");continue}if(o.board[n][l]){console.log("Destination square occupied");continue}const s=(n+l)%2===0;console.log("Square color check:",{newRow:n,newCol:l,sum:n+l,isBlackSquare:s}),s?(a.push({row:n,col:l}),console.log("Valid move found:",{row:n,col:l})):console.log("Not a black square")}return console.log("Final valid moves:",a),a},p=async(r,n)=>{var p,m;if(!o.gameId||"finished"===o.status)return;const g=null===(p=o.board)||void 0===p?void 0:null===(m=p[r])||void 0===m?void 0:m[n];if(console.log("Clicked square:",{row:r,col:n,piece:g}),console.log("Game state:",{currentPlayer:o.currentPlayer,selectedSquare:t,validMoves:l}),!t){if(!g)return void console.log("Clicked empty square");if(!("red"===o.currentPlayer&&"r"===g.toLowerCase()||"black"===o.currentPlayer&&"b"===g.toLowerCase()))return void alert("You can only move your own pieces!");const e=u(r,n);return console.log("Calculated valid moves:",e),0===e.length?void alert("This piece has no valid moves!"):(a({row:r,col:n,piece:g}),void c(e))}if(t.row===r&&t.col===n)return console.log("Deselecting piece"),a(null),void c([]);const f=l.some(o=>o.row===r&&o.col===n);if(console.log("Move validation:",{isValidDestination:f,selectedSquare:t,targetSquare:{row:r,col:n}}),!f)return console.log("Invalid move - not in valid moves list"),a(null),void c([]);try{const l={fromRow:t.row,fromCol:t.col,toRow:r,toCol:n};console.log("Sending move to API:",l);const p=await fetch("".concat(i,"/games/").concat(o.gameId),{method:"PUT",headers:{"Content-Type":"application/json",Accept:"application/json"},mode:"cors",body:JSON.stringify(l)});if(!p.ok){const o=await p.json();throw console.error("API Error:",{status:p.status,statusText:p.statusText,errorData:o}),new Error(o.error||"Invalid move")}const m=await p.json();console.log("Move successful:",m),e(m),m.hasMoreJumps?(a({row:r,col:n,piece:m.board[r][n]}),c(u(r,n))):(a(null),c([]));const g=(()=>{const o=d("r"),e=d("b");return console.log("Piece count:",{red:o,black:e}),0===o?"black":0===e?"red":null})();g&&e(o=>Object(s.a)(Object(s.a)({},o),{},{status:"finished",winner:g}))}catch(w){console.error("Error making move:",w),alert(w instanceof Error?w.message:"Invalid move. Please try again."),a(null),c([])}};return n.a.createElement("div",{className:"App",style:{padding:"20px",textAlign:"center"}},n.a.createElement("h1",null,"Checkers Game"),n.a.createElement("div",{className:"game-status",style:{fontSize:"1.5em",marginBottom:"20px",fontWeight:"bold",color:"finished"===o.status?"#4CAF50":"#2196F3"}},"finished"===o.status&&o.winner?"Game Over - ".concat(o.winner.charAt(0).toUpperCase()+o.winner.slice(1)," Wins!"):"Current Turn: ".concat(o.currentPlayer.charAt(0).toUpperCase()+o.currentPlayer.slice(1))),n.a.createElement("div",{className:"game-board",style:{display:"inline-block",border:"2px solid #333",backgroundColor:"#fff"}},o.board.map((o,e)=>n.a.createElement("div",{key:e,className:"board-row",style:{display:"flex"}},o.map((o,r)=>{const a=(e+r)%2===0,s=(null===t||void 0===t?void 0:t.row)===e&&(null===t||void 0===t?void 0:t.col)===r,c=l.some(o=>o.row===e&&o.col===r);return n.a.createElement("div",{key:r,onClick:()=>p(e,r),style:{width:"60px",height:"60px",backgroundColor:a?"#666":"#fff",border:s?"3px solid yellow":"1px solid #999",display:"flex",justifyContent:"center",alignItems:"center",cursor:"pointer",position:"relative",boxSizing:"border-box"}},o&&n.a.createElement("div",{style:{width:"80%",height:"80%",borderRadius:"50%",backgroundColor:"r"===o.toLowerCase()?"#ff4444":"#333",border:"2px solid #fff",boxShadow:"0 0 10px rgba(0,0,0,0.3)",position:"relative"}},o===o.toUpperCase()&&n.a.createElement("div",{style:{position:"absolute",top:"50%",left:"50%",transform:"translate(-50%, -50%)",color:"r"===o.toLowerCase()?"#ffcccc":"#666",fontSize:"24px"}},"\u2654")),c&&n.a.createElement("div",{style:{position:"absolute",width:"20px",height:"20px",borderRadius:"50%",backgroundColor:"rgba(0, 255, 0, 0.5)",border:"2px solid rgba(0, 255, 0, 0.8)"}}))})))),n.a.createElement("div",{style:{marginTop:"20px"}},n.a.createElement("button",{onClick:async()=>{try{const t=await fetch("".concat(i,"/games"),{method:"POST",headers:{"Content-Type":"application/json",Accept:"application/json"},mode:"cors"});if(!t.ok)throw new Error("Failed to create game");const r=await t.json();if(console.log("API Response:",r),"string"===typeof r){const o=JSON.parse(r);console.log("Parsed new game state:",o),e(o)}else console.log("Setting game state directly:",r),e(r);a(null),c([])}catch(o){console.error("Error creating game:",o),alert("Failed to create new game. Please try again.")}},style:{padding:"10px 20px",fontSize:"16px",backgroundColor:"#4CAF50",color:"white",border:"none",borderRadius:"4px",cursor:"pointer",marginBottom:"20px"}},"finished"===o.status?"Play Again":o.gameId?"Restart Game":"New Game")))};l.a.createRoot(document.getElementById("root")).render(n.a.createElement(n.a.StrictMode,null,n.a.createElement(c,null)))},4:function(o,e,t){o.exports=t(13)}},[[4,1,2]]]);
//# sourceMappingURL=main.8da51060.chunk.js.map