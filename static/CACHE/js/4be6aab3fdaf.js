!function(a,b){"function"==typeof define&&define.amd?define([],b):"undefined"!=typeof module&&module.exports?module.exports=b():a.ReconnectingWebSocket=b()}(this,function(){function a(b,c,d){function l(a,b){var c=document.createEvent("CustomEvent");return c.initCustomEvent(a,!1,!1,b),c}var e={debug:!1,automaticOpen:!0,reconnectInterval:1e3,maxReconnectInterval:3e4,reconnectDecay:1.5,timeoutInterval:2e3};d||(d={});for(var f in e)this[f]="undefined"!=typeof d[f]?d[f]:e[f];this.url=b,this.reconnectAttempts=0,this.readyState=WebSocket.CONNECTING,this.protocol=null;var h,g=this,i=!1,j=!1,k=document.createElement("div");k.addEventListener("open",function(a){g.onopen(a)}),k.addEventListener("close",function(a){g.onclose(a)}),k.addEventListener("connecting",function(a){g.onconnecting(a)}),k.addEventListener("message",function(a){g.onmessage(a)}),k.addEventListener("error",function(a){g.onerror(a)}),this.addEventListener=k.addEventListener.bind(k),this.removeEventListener=k.removeEventListener.bind(k),this.dispatchEvent=k.dispatchEvent.bind(k),this.open=function(b){h=new WebSocket(g.url,c||[]),b||k.dispatchEvent(l("connecting")),(g.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","attempt-connect",g.url);var d=h,e=setTimeout(function(){(g.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","connection-timeout",g.url),j=!0,d.close(),j=!1},g.timeoutInterval);h.onopen=function(){clearTimeout(e),(g.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","onopen",g.url),g.protocol=h.protocol,g.readyState=WebSocket.OPEN,g.reconnectAttempts=0;var d=l("open");d.isReconnect=b,b=!1,k.dispatchEvent(d)},h.onclose=function(c){if(clearTimeout(e),h=null,i)g.readyState=WebSocket.CLOSED,k.dispatchEvent(l("close"));else{g.readyState=WebSocket.CONNECTING;var d=l("connecting");d.code=c.code,d.reason=c.reason,d.wasClean=c.wasClean,k.dispatchEvent(d),b||j||((g.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","onclose",g.url),k.dispatchEvent(l("close")));var e=g.reconnectInterval*Math.pow(g.reconnectDecay,g.reconnectAttempts);setTimeout(function(){g.reconnectAttempts++,g.open(!0)},e>g.maxReconnectInterval?g.maxReconnectInterval:e)}},h.onmessage=function(b){(g.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","onmessage",g.url,b.data);var c=l("message");c.data=b.data,k.dispatchEvent(c)},h.onerror=function(b){(g.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","onerror",g.url,b),k.dispatchEvent(l("error"))}},1==this.automaticOpen&&this.open(!1),this.send=function(b){if(h)return(g.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","send",g.url,b),h.send(b);throw"INVALID_STATE_ERR : Pausing to reconnect websocket"},this.close=function(a,b){"undefined"==typeof a&&(a=1e3),i=!0,h&&h.close(a,b)},this.refresh=function(){h&&h.close()}}return a.prototype.onopen=function(){},a.prototype.onclose=function(){},a.prototype.onconnecting=function(){},a.prototype.onmessage=function(){},a.prototype.onerror=function(){},a.debugAll=!1,a.CONNECTING=WebSocket.CONNECTING,a.OPEN=WebSocket.OPEN,a.CLOSING=WebSocket.CLOSING,a.CLOSED=WebSocket.CLOSED,a});var UTILS_N=UTILS_N||(function(){var _args={};var _showLimitChar=90;return{init:function(args){_args=args;},conn_socket:function(){var ws_scheme=window.location.protocol=="https:"?"wss":"ws";var ws_path=ws_scheme+'://'+window.location.host+window.location.pathname+"notification/";console.log("Connecting to "+ws_path);var socket=new ReconnectingWebSocket(ws_path);socket.onmessage=function(message){var data=JSON.parse(message.data);console.log(data);var content='<li class=\"collection-item avatar\" data-id="'+data.id+'">';content+='<a onclick="AJAX_mark_read(this)" class="fa fa-remove" id="mark-as-read-notification" data-notification="'+data.slug+'"/></a>';if(data.actor_avatar!==null&&typeof data.actor_avatar!=='undefined'){content=content+" <img class=\"circle\" src=\""+data.actor_avatar+'"/>';}
if(typeof data.actor!=='undefined'&&data.level!=='new_follow'){content=content+"<a class=\"title\" href=\"/profile/"+data.actor+'" >'+data.actor+'</a>';}
if(typeof data.verb!=='undefined'){content=content+" <span class=\"title\"/>"+data.verb+'</span>';}
if(typeof data.target!=='undefined'){content=content+" "+data.target;}
if(typeof data.description!=='undefined'&&data.description!=null){content=content+" "+data.description;}
if(typeof data.timestamp!=='undefined'){content=content+"<p><i>"+data.timestamp+'</i></p>';}
if(typeof data.level!=='undefined'&&data.level=='friendrequest'){content=content+" <div class=\"notification-buttons\"><"+'button data-notification="'+data.slug+'" onclick="AJAX_respondFriendRequest(\''+data.actor_object_id+'\',\''+"accept"+'\',\''+data.id+'\'); AJAX_delete_notification(\''+data.slug+'\',\''+data.id+'\')" class="accept-response waves-effect waves-light btn white-text green"><i class="material-icons">done</i></button>\<'+'button data-notification="'+data.slug+'"onclick="AJAX_respondFriendRequest(\''+data.actor_object_id+'\',\''+"rejected"+'\',\''+data.id+'\'); AJAX_delete_notification(\''+data.slug+'\',\''+data.id+'\')" class="rejected-response waves-effect waves-light btn white-text red"> <i class="material-icons">cancel</i></button>\<'+'/div>';}
if(typeof data.actor!=='undefined'&&typeof data.verb!=='undefined'){Materialize.toast('@'+data.actor+' - '+data.verb,4000);}
content+="<a href=\"#!\" class=\"secondary-content\"><i class=\"material-icons\">people<\/i><\/a></li>";var list_notifications=$('#list-notify');var existing=$(list_notifications).find("[data-id='"+data.id+"']");if(existing.length){existing.html(content);}else{$(list_notifications).prepend(content);var live_notify=$('#live_notify_badge');$(live_notify).html(parseInt($(live_notify).html(),10)+1);}};if(socket.readyState==WebSocket.OPEN)socket.onopen();socket.onclose=function(){console.log("No connected.");};}};}());