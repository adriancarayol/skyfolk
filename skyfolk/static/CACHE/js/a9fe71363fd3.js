;$(document).ready(function(){$('select').material_select();$('ul.tabs').tabs();$('#btn-upload-photo').on('click',function(){$('#upload_photo').toggle();});$('#close_upload_form, #close_upload_zip_form, #close_upload_video_form').on('click',function(){$('#upload_photo').toggle();});$('#del-photo').click(AJAX_delete_photo);$('#del-video').click(AJAX_delete_video);$("#edit-video").click(function(){$(this).text(function(i,text){return text==="Editar"?"No editar":"Editar";});$('#wrapper-edit-form').toggle();return false;});$("#edit-photo").click(function(){$(this).text(function(i,text){return text==="Editar"?"No editar":"Editar";});$('#wrapper-edit-form').toggle();return false;});$('.tags-content').on('click','blockquote',function(){$(this).nextAll('input').click();});$('#crop-image-preview').find('.close-crop-image').on('click',function(){$('#crop-image-preview').hide();$('.avatar-form .is-cutted').val('false');});$('#crop-image-preview').find('#cut-done').on('click',function(){$('#crop-image-preview').hide();$('.avatar-form .is-cutted').val('true');});$(this).on('keydown',function(e){var key=e.keyCode||e.which;if(key==27){$('#upload_photo').hide();$('#crop-image-preview').hide();$('.avatar-form .is-cutted').val('false');}});$('#form-video').submit(function(e){e.preventDefault();var url=$(this).attr('action');var data=new FormData($(this).get(0));$.ajax({url:url,type:'POST',data:data,dataType:'json',async:true,contentType:false,enctype:'multipart/form-data',processData:false,success:function(data){console.log(data);if(data.result===true){}else{swal({title:"¡Ups!.",type:'error',text:data.message,timer:4000,showConfirmButton:true});}},error:function(rs,e){swal(rs.responseText+" "+e);}});});});function AJAX_delete_photo(){var _id=$('.photo-body').attr('data-id');$.ajax({url:'/delete/photo/',type:'DELETE',data:{'id':_id,'csrfmiddlewaretoken':csrftoken},dataType:'json',success:function(json){swal({title:"Photo was deleted.",text:json.msg,timer:2500,showConfirmButton:true},function(){window.location.replace('/multimedia/'+json.author+'/');});},error:function(rs,e){swal(rs.responseText+" "+e);}});}
function AJAX_delete_video(){var _id=$('.photo-body').attr('data-id');$.ajax({url:'/delete/video/',type:'DELETE',data:{'id':_id,'csrfmiddlewaretoken':csrftoken},dataType:'json',success:function(json){swal({title:"Photo was deleted.",text:json.msg,timer:2500,showConfirmButton:true},function(){window.location.replace('/multimedia/'+json.author+'/');});},error:function(rs,e){swal(rs.responseText+" "+e);}});};var max_height_comment=60;$(document).ready(function(){var tab_messages=$(this);var wrapper_shared_pub=$('#share-publication-wrapper');$(tab_messages).find('.wrapper').each(function(){var comment=$(this).find('.wrp-comment');var show=$(this).find('.show-more a');if($(comment).height()>max_height_comment){$(show).show();$(comment).css('height','2.6em');}else{}});$(tab_messages).on('click','.show-more a',function(){var $this=$(this);var $content=$this.parent().prev("div.comment").find(".wrp-comment");var linkText=$this.text().toUpperCase();if(linkText==="+ MOSTRAR MÁS"){linkText="- Mostrar menos";$content.css('height','auto');}else{linkText="+ Mostrar más";$content.css('height','2.6em');}
$this.text(linkText);return false;});$(tab_messages).on('click','.wrapper .zoom-pub',function(){var caja_pub=$(this).closest('.wrapper');expandComment(caja_pub);});function expandComment(caja_pub){var id_pub=$(caja_pub).attr('id').split('-')[1];window.location.href='/publication_pdetail/'+id_pub;}
$(tab_messages).on('click','.options_comentarios .add-timeline',function(){var tag=$(this);wrapper_shared_pub.find('#id_pk').val($(tag).data('id'));wrapper_shared_pub.show();});$(wrapper_shared_pub).find('#share_publication_form').on('submit',function(event){event.preventDefault();var content=$(this).serialize();var pub_id=wrapper_shared_pub.find('#id_pk').val();var tag=$('#pub-'+pub_id).find('.add-timeline').first();AJAX_add_timeline_gallery(pub_id,tag,content);});$('#close_share_publication').click(function(){wrapper_shared_pub.hide();$wrapper_shared_pub.find('#id_pk').val('');});$(tab_messages).on('click','.options_comentarios .remove-timeline',function(){var tag=$(this);AJAX_remove_timeline_gallery(tag.data('id'),tag);});$(tab_messages).on('click','.options_comentarios .reply-comment',function(){var id_=$(this).attr("id").slice(6);$("#"+id_).slideToggle("fast");});$(tab_messages).on('click','button.enviar',function(event){event.preventDefault();var parent_pk=$(this).attr('id').split('-')[1];var form=$(this).parent();AJAX_submit_photo_publication(form,'reply',parent_pk);});$(tab_messages).on('click','.options_comentarios .like-comment',function(){var caja_publicacion=$(this).closest('.wrapper');var heart=$(this);AJAX_add_like_gallery(caja_publicacion,heart,"publication");});$(tab_messages).on('click','.options_comentarios .hate-comment',function(){var caja_publicacion=$(this).closest('.wrapper');var heart=$(this);AJAX_add_hate_gallery(caja_publicacion,heart,"publication");});$(tab_messages).on('click','.options_comentarios .trash-comment',function(){var caja_publicacion=$(this).closest('.wrapper');swal({title:"Are you sure?",text:"You will not be able to recover this publication!",type:"warning",animation:"slide-from-top",showConfirmButton:true,showCancelButton:true,confirmButtonColor:"#DD6B55",confirmButtonText:"Yes, delete it!",cancelButtonText:"No God, please no!",closeOnConfirm:true},function(isConfirm){if(isConfirm){AJAX_delete_publication_gallery(caja_publicacion);}});});$("#tab-messages").find('#message-photo-form').on('submit',function(event){event.preventDefault();var form=$('#messages-wrapper').find('#message-photo-form');AJAX_submit_photo_publication(form,'publication');});$(tab_messages).on('click','.edit-comment',function(){var id=$(this).attr('data-id');$("#p_author-controls-"+id).slideToggle("fast");});$(tab_messages).on('click','.edit-comment-btn',function(event){event.preventDefault();var edit=$(this).closest('form').serialize();AJAX_edit_publication_gallery(edit);});$(tab_messages).on('click','.load_more_descendants',function(e){e.preventDefault();var loader=$(this).next().find('.load_publications_descendants');var pub_id=$(this).attr("data-id");var page=$('.page_for_'+pub_id).last().val();if(typeof page==='undefined')
page=1;AJAX_load_descendants_gallery(pub_id,loader,page,this);});$('#messages-wrapper').on('click','#load-comments',function(e){e.preventDefault();$.ajax({type:"GET",url:$(this).attr('href'),success:function(data)
{$('#load-comments').remove();$('.loading_publications').before(data);}});});});function AJAX_submit_photo_publication(obj_form,type,pks){var form=new FormData($(obj_form).get(0));form.append('csrfmiddlewaretoken',getCookie('csrftoken'));type=typeof type!=='undefined'?type:"reply";$.ajax({url:'/publication_p/',type:'POST',data:form,async:true,dataType:"json",contentType:false,enctype:'multipart/form-data',processData:false,success:function(data){var msg=data.msg;if(typeof(msg)!=='undefined'&&msg!==null){swal({title:"",text:msg,customClass:'default-div',type:"success"});}
if(type==="reply"){var caja_comentarios=$('#caja-comentario-'+pks);$(caja_comentarios).find('.message-reply').val('');$(caja_comentarios).fadeOut();}else if(type==="publication"){$('#message-photo').val('');}},error:function(data,textStatus,jqXHR){var errors=[];$.each(data.responseJSON,function(i,val){errors.push(val);});swal({title:"Tenemos un problema...",customClass:'default-div',text:errors.join(),timer:4000,showConfirmButton:true});}}).done(function(){})}
function AJAX_delete_publication_gallery(caja_publicacion){var id_pub=$(caja_publicacion).attr('id').split('-')[1];var id_user=$(caja_publicacion).data('id');var data={userprofile_id:id_user,publication_id:id_pub,'csrfmiddlewaretoken':csrftoken};$.ajax({url:'/publication_p/delete/',type:'POST',dataType:'json',data:data,success:function(data){if(data===true){$(caja_publicacion).closest('.infinite-item').remove();$(".infinite-container").find(`[data-parent='${id_pub}']`).closest('.infinite-item').remove();}else{swal({title:"Fail",customClass:'default-div',text:"Failed to delete publish.",type:"error"});}},error:function(rs,e){}});}
function AJAX_add_like_gallery(caja_publicacion,heart,type){var id_pub;if(type.localeCompare("publication")==0){id_pub=$(caja_publicacion).attr('id').split('-')[1];}else if(type.localeCompare("timeline")==0){id_pub=$(caja_publicacion).attr('data-publication');}
var id_user=$(caja_publicacion).attr('data-id');var data={userprofile_id:id_user,publication_id:id_pub,'csrfmiddlewaretoken':csrftoken};$.ajax({url:'/publication_p/add_like/',type:'POST',dataType:'json',data:data,success:function(data){var response=data.response;var status=data.statuslike;var numLikes=heart.find('.like-value');var countLikes=numLikes.text();if(response==true){if(!countLikes||(Math.floor(countLikes)==countLikes&&$.isNumeric(countLikes))){if(status==1){heart.css('color','#f06292');countLikes++;}else if(status==2){heart.css('color','#555');countLikes--;}else if(status==3){heart.css('color','#f06292');var hatesObj=heart.prev();var hates=hatesObj.find(".hate-value");var countHates=hates.text();countHates--;if(countHates<=0){hates.text('');}else
hates.text(countHates);$(hatesObj).css('color','#555');countLikes++;}
if(countLikes<=0){numLikes.text('');}else{numLikes.text(countLikes);}}else{if(status==1)
heart.css('color','#f06292');if(status==2)
heart.css('color','#555');}}else{swal({title:":-(",text:"¡No puedes dar me gusta a este comentario!",timer:4000,customClass:'default-div',animation:"slide-from-bottom",showConfirmButton:false,type:"error"});}},error:function(rs,e){}});}
function AJAX_add_hate_gallery(caja_publicacion,heart,type){var id_pub;if(type.localeCompare("publication")==0){id_pub=$(caja_publicacion).attr('id').split('-')[1];}else if(type.localeCompare("timeline")==0){id_pub=$(caja_publicacion).attr('data-publication');}
var id_user=$(caja_publicacion).attr('id');var data={userprofile_id:id_user,publication_id:id_pub,'csrfmiddlewaretoken':csrftoken};$.ajax({url:'/publication_p/add_hate/',type:'POST',dataType:'json',data:data,success:function(data){var statusOk=1;var statusNo=2;var statusInLike=3;var response=data.response;var status=data.statuslike;var numHates=heart.find(".hate-value");var countHates=numHates.text();if(response==true){if(!countHates||(Math.floor(countHates)==countHates&&$.isNumeric(countHates))){if(status===statusOk){heart.css('color','#ba68c8');countHates++;}else if(status===statusNo){heart.css('color','#555');countHates--;}else if(status===statusInLike){heart.css('color','#ba68c8');countHates++;var likesObj=heart.next();var likes=likesObj.find(".like-value");var countLikes=likes.text();countLikes--;if(countLikes<=0){likes.text('');}else
likes.text(countLikes);$(likesObj).css('color','#555');}
if(countHates<=0){numHates.text("");}else{numHates.text(countHates);}}else{if(status===statusOk){heart.css('color','#ba68c8');}else if(status===statusNo){heart.css('color','#555');}}}else{swal({title:":-(",text:"¡No puedes dar no me gusta a este comentario!",timer:4000,customClass:'default-div',animation:"slide-from-bottom",showConfirmButton:false,type:"error"});}},error:function(rs,e){}});}
function AJAX_add_timeline_gallery(pub_id,tag,data_pub){var shared_tag=tag.find('.share-values');var count_shared=$(shared_tag).text();count_shared=count_shared.replace(/ /g,'');$.ajax({url:'/publication_p/share/publication/',type:'POST',dataType:'json',data:data_pub,success:function(response){if(response===true){if(!count_shared||(Math.floor(count_shared)==count_shared&&$.isNumeric(count_shared))){count_shared++;if(count_shared>0){$(shared_tag).text(" "+count_shared);}else{$(shared_tag).text(" ");}}
$(tag).attr("class","remove-timeline");$(tag).css('color','#bbdefb');$('#share-publication-wrapper').hide();}else{swal({title:"Fail",customClass:'default-div',text:"Failed to add to timeline.",type:"error"});}},error:function(rs,e){}});}
function AJAX_remove_timeline_gallery(pub_id,tag){var shared_tag=$(tag).find('.share-values');var count_shared=$(shared_tag).text();count_shared=count_shared.replace(/ /g,'');$.ajax({url:'/publication_p/delete/share/publication/',type:'POST',dataType:'json',data:{'pk':pub_id},success:function(data){var response=data.response;if(response===true){if(!count_shared||(Math.floor(count_shared)==count_shared&&$.isNumeric(count_shared))){count_shared--;if(count_shared>0){$(shared_tag).text(" "+count_shared);}else{$(shared_tag).text(" ");}}
$(tag).attr("class","add-timeline");$(tag).css('color','#555');}else{swal({title:"Fail",customClass:'default-div',text:"Failed to add to timeline.",type:"error"});}},error:function(jqXHR,textStatus,errorThrown){}});}
function AJAX_edit_publication_gallery(data){$.ajax({url:'/publication_p/edit/',type:'POST',dataType:'json',data:data,success:function(data){var response=data.data;if(response===false){swal({title:"Fail",customClass:'default-div',text:"Failed to edit publish.",type:"error"});}},error:function(rs,e){}});}
function AJAX_load_descendants_gallery(pub,loader,page,btn){$.ajax({url:'/publication_p/load_descendants/?pubid='+pub+'&page='+page,type:'GET',dataType:'html',beforeSend:function(){$(loader).fadeIn();},success:function(data){var $existing=$('#pub-'+pub);var $children_list=$existing.find('.children').first();if(!$children_list.length){$existing.find('.wrapper-reply').after('<ul class="children"></ul>');$children_list=$existing.find('.children').first();}
$children_list.append(data);var $child_count=$(btn).find('.child_count');var $result_child_count=parseInt($child_count.html(),10)-$('.childs_for_'+pub).last().val();if($result_child_count>0)
$($child_count).html($result_child_count);else
$(btn).remove();},complete:function(){$(loader).fadeOut();},error:function(rs,e){}});};var max_height_comment=60;var UTILS=UTILS||(function(){var _args={};var _showLimitChar=90;return{init:function(args){_args=args;},conn_socket:function(){var ws_scheme=window.location.protocol=="https:"?"wss":"ws";var ws_path=ws_scheme+'://'+window.location.host+window.location.pathname+"stream/";console.log("Connecting to "+ws_path);var socket=new ReconnectingWebSocket(ws_path);socket.onmessage=function(message){var data=JSON.parse(message.data);if(data.type==="pub"){var existing=$('#pub-'+data.id);var no_comments=$('#without-comments');no_comments.remove();if(existing.length){existing.closest('.row').replaceWith(data.content);}else{var $parent=$('#pub-'+data.parent_id);if($parent.length){if(data.level==1||data.level==2){var $children_list=$parent.find('.children').first();if(!$children_list.length){$children_list=$parent.find('.wrapper-reply').after('<ul class="children"></ul>');}
$children_list.prepend(data.content);}else{$parent.closest('.row').after(data.content);}}else $("#messages-wrapper").prepend(data.content);}}else if(data.type==="video"){var existing_pub=$('#pub-'+data.id);if(existing_pub.length){var card_content=$(existing_pub).find('.publication-content');var videos=$(existing_pub).find('.videos');if(videos.length){$(videos).append('<div class="col s4"><video class="responsive-video" controls loop><source src="/media/'+data.video+'" type="video/mp4"></video></div>');}else{var images=$(existing_pub).find('.images');if(images.length){$(images).after('<div class="row videos"><div class="col s4"><video class="responsive-video" controls loop><source src="/media/'+data.video+'" type="video/mp4"></video></div></div>');}
$(card_content).after('<div class="row videos"><div class="col s4"><video class="responsive-video" controls loop><source src="/media/'+data.video+'" type="video/mp4"></video></div></div>');}}}else{var content="";content+="                <div class=\"wrapper-reply\">";content+="";content+="";content+="                <div class=\"comment-reply\">";content+='                <div class=\"avatar-reply\"><img src="'+data.avatar_path+'" alt="'+data.p_author_username+'" width="120" height="120"><\/div>';content+="                    <div class=\"author-reply\">";content+='                      <a href="/profile/'+data.p_author_username+'">'+data.p_author_username+'</a>';content+='                      <i class="reply-created">'+data.created+'<\/i>';content+="                    </div>";content+='                      <div class="content-reply">'+data.content+'</div>';content+="                </div>";content+="";content+="                </div>";content+="    </div>";var pub=$('#pub-'+data.parent);$(pub).append(content);}};if(socket.readyState==WebSocket.OPEN)socket.onopen();socket.onclose=function(){console.log("No connected.");};}};}());;!function(a,b){"function"==typeof define&&define.amd?define([],b):"undefined"!=typeof module&&module.exports?module.exports=b():a.ReconnectingWebSocket=b()}(this,function(){function a(b,c,d){function l(a,b){var c=document.createEvent("CustomEvent");return c.initCustomEvent(a,!1,!1,b),c}var e={debug:!1,automaticOpen:!0,reconnectInterval:1e3,maxReconnectInterval:3e4,reconnectDecay:1.5,timeoutInterval:2e3};d||(d={});for(var f in e)this[f]="undefined"!=typeof d[f]?d[f]:e[f];this.url=b,this.reconnectAttempts=0,this.readyState=WebSocket.CONNECTING,this.protocol=null;var h,g=this,i=!1,j=!1,k=document.createElement("div");k.addEventListener("open",function(a){g.onopen(a)}),k.addEventListener("close",function(a){g.onclose(a)}),k.addEventListener("connecting",function(a){g.onconnecting(a)}),k.addEventListener("message",function(a){g.onmessage(a)}),k.addEventListener("error",function(a){g.onerror(a)}),this.addEventListener=k.addEventListener.bind(k),this.removeEventListener=k.removeEventListener.bind(k),this.dispatchEvent=k.dispatchEvent.bind(k),this.open=function(b){h=new WebSocket(g.url,c||[]),b||k.dispatchEvent(l("connecting")),(g.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","attempt-connect",g.url);var d=h,e=setTimeout(function(){(g.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","connection-timeout",g.url),j=!0,d.close(),j=!1},g.timeoutInterval);h.onopen=function(){clearTimeout(e),(g.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","onopen",g.url),g.protocol=h.protocol,g.readyState=WebSocket.OPEN,g.reconnectAttempts=0;var d=l("open");d.isReconnect=b,b=!1,k.dispatchEvent(d)},h.onclose=function(c){if(clearTimeout(e),h=null,i)g.readyState=WebSocket.CLOSED,k.dispatchEvent(l("close"));else{g.readyState=WebSocket.CONNECTING;var d=l("connecting");d.code=c.code,d.reason=c.reason,d.wasClean=c.wasClean,k.dispatchEvent(d),b||j||((g.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","onclose",g.url),k.dispatchEvent(l("close")));var e=g.reconnectInterval*Math.pow(g.reconnectDecay,g.reconnectAttempts);setTimeout(function(){g.reconnectAttempts++,g.open(!0)},e>g.maxReconnectInterval?g.maxReconnectInterval:e)}},h.onmessage=function(b){(g.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","onmessage",g.url,b.data);var c=l("message");c.data=b.data,k.dispatchEvent(c)},h.onerror=function(b){(g.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","onerror",g.url,b),k.dispatchEvent(l("error"))}},1==this.automaticOpen&&this.open(!1),this.send=function(b){if(h)return(g.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","send",g.url,b),h.send(b);throw"INVALID_STATE_ERR : Pausing to reconnect websocket"},this.close=function(a,b){"undefined"==typeof a&&(a=1e3),i=!0,h&&h.close(a,b)},this.refresh=function(){h&&h.close()}}return a.prototype.onopen=function(){},a.prototype.onclose=function(){},a.prototype.onconnecting=function(){},a.prototype.onmessage=function(){},a.prototype.onerror=function(){},a.debugAll=!1,a.CONNECTING=WebSocket.CONNECTING,a.OPEN=WebSocket.OPEN,a.CLOSING=WebSocket.CLOSING,a.CLOSED=WebSocket.CLOSED,a});