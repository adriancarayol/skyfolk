;$(document).ready(function(){$('select').material_select();$('ul.tabs').tabs();$('#btn-upload-photo').on('click',function(){$('#upload_photo').toggle();});$('#close_upload_form, #close_upload_zip_form').on('click',function(){$('#upload_photo').toggle();});$('#del-photo').click(AJAX_delete_photo);$("#edit-photo").click(function(){$(this).text(function(i,text){return text==="Editar"?"No editar":"Editar";});$('#wrapper-edit-form').toggle();return false;});$('.tags-content').on('click','blockquote',function(){$(this).nextAll('input').click();});$('#crop-image-preview').find('.close-crop-image').on('click',function(){$('#crop-image-preview').hide();$('.avatar-form .is-cutted').val('false');});$('#crop-image-preview').find('#cut-done').on('click',function(){$('#crop-image-preview').hide();$('.avatar-form .is-cutted').val('true');});$(this).on('keydown',function(e){var key=e.keyCode||e.which;if(key==27){$('#upload_photo').hide();$('#crop-image-preview').hide();$('.avatar-form .is-cutted').val('false');}});$('#tab-messages').find('#message-photo-form').on('submit',function(event){event.preventDefault();var form=$('#messages-wrapper').find('#message-photo-form');AJAX_submit_photo_publication(form,'publication');});});function AJAX_delete_photo(){var _id=$('.photo-body').attr('data-id');$.ajax({url:'/delete/photo/',type:'DELETE',data:{'id':_id,'csrfmiddlewaretoken':csrftoken},dataType:'json',success:function(json){swal({title:"Photo was deleted.",text:json.msg,timer:2500,showConfirmButton:true},function(){window.location.replace('/multimedia/'+json.author+'/');});},error:function(rs,e){swal(rs.responseText+" "+e);}});};var max_height_comment=60;$(document).ready(function(){var tab_messages=$(this);var wrapper_shared_pub=$('#share-publication-wrapper');$(tab_messages).find('.wrapper').each(function(){var comment=$(this).find('.wrp-comment');var show=$(this).find('.show-more a');if($(comment).height()>max_height_comment){$(show).show();$(comment).css('height','2.6em');}else{}});$(tab_messages).on('click','.show-more a',function(){var $this=$(this);var $content=$this.parent().prev("div.comment").find(".wrp-comment");var linkText=$this.text().toUpperCase();if(linkText==="+ MOSTRAR MÁS"){linkText="- Mostrar menos";$content.css('height','auto');}else{linkText="+ Mostrar más";$content.css('height','2.6em');}
$this.text(linkText);return false;});$(tab_messages).on('click','.wrapper .zoom-pub',function(){var caja_pub=$(this).closest('.wrapper');expandComment(caja_pub);});function expandComment(caja_pub){var id_pub=$(caja_pub).attr('id').split('-')[1];window.location.href='/publication_pdetail/'+id_pub;}
$(tab_messages).on('click','.options_comentarios .add-timeline',function(){var tag=this;$(wrapper_shared_pub).attr('data-id',$(tag).attr('data-id'));$(wrapper_shared_pub).show();});$(wrapper_shared_pub).find('#share_publication_form').on('submit',function(event){event.preventDefault();var content=$(wrapper_shared_pub).find('#shared_comment_content').val();var pub_id=$(wrapper_shared_pub).attr('data-id');var tag=$('#pub-'+pub_id).find('.add-timeline').first();AJAX_add_timeline_gallery(pub_id,tag,content);});$('#close_share_publication').click(function(){$(wrapper_shared_pub).hide();});$(tab_messages).on('click','.options_comentarios .remove-timeline',function(){var caja_publicacion=$(this).closest('.wrapper');var tag=this;AJAX_add_timeline_gallery($(caja_publicacion).attr('id').split('-')[1],tag,null);});$(tab_messages).on('click','.options_comentarios .fa-reply',function(){var id_=$(this).attr("id").slice(6);$("#"+id_).slideToggle("fast");});$(tab_messages).on('click','button.enviar',function(event){event.preventDefault();var parent_pk=$(this).attr('id').split('-')[1];var form=$(this).parent();AJAX_submit_photo_publication(form,'reply',parent_pk);});$(tab_messages).on('click','.options_comentarios .like-comment',function(){var caja_publicacion=$(this).closest('.wrapper');var heart=this;AJAX_add_like_gallery(caja_publicacion,heart,"publication");});$(tab_messages).on('click','.options_comentarios .hate-comment',function(){var caja_publicacion=$(this).closest('.wrapper');var heart=this;AJAX_add_hate_gallery(caja_publicacion,heart,"publication");});$(tab_messages).on('click','.options_comentarios .fa-trash',function(){var caja_publicacion=$(this).closest('.wrapper');swal({title:"Are you sure?",text:"You will not be able to recover this publication!",type:"warning",animation:"slide-from-top",showConfirmButton:true,showCancelButton:true,confirmButtonColor:"#DD6B55",confirmButtonText:"Yes, delete it!",cancelButtonText:"No God, please no!",closeOnConfirm:true},function(isConfirm){if(isConfirm){AJAX_delete_publication_gallery(caja_publicacion);}});});$(tab_messages).on('click','.edit-comment',function(){var id=$(this).attr('data-id');$("#p_author-controls-"+id).slideToggle("fast");});$(tab_messages).on('click','.edit-comment-btn',function(event){event.preventDefault();var id=$(this).attr('data-id');var content=$(this).closest('#p_author-controls-'+id).find('#id_caption-'+id).val();AJAX_edit_publication_gallery(id,content);});$(tab_messages).on('click','.load_more_descendants',function(){var loader=$(this).next().find('.load_publications_descendants');$(loader).fadeIn();var last_pub=$(loader).closest('.row').prev('.children').find('.wrapper').last().attr('id');var last_pub_id="";if(last_pub){last_pub_id=last_pub.toString().split('-')[1];}
AJAX_load_descendants_gallery($(this).attr("data-id"),loader,last_pub_id,this);return false;});$('#load-comments').on('click',function(e){e.preventDefault();$.ajax({type:"GET",url:$(this).attr('href'),success:function(data)
{var $load_btn=$(data).find('#load-comments');if($load_btn.length){$('#load-comments').replaceWith($load_btn);$('#load-comments').before(data);}else{$('#messages-wrapper').append(data);}}});});});function AJAX_submit_photo_publication(obj_form,type,pks){var form=new FormData($(obj_form).get(0));form.append('csrfmiddlewaretoken',getCookie('csrftoken'));type=typeof type!=='undefined'?type:"reply";$.ajax({url:'/publication_p/',type:'POST',data:form,async:true,dataType:"json",contentType:false,enctype:'multipart/form-data',processData:false,success:function(data){var response=data.response;var msg=data.msg;if(response===true&&(typeof(msg)!=='undefined'&&msg!==null)){swal({title:"",text:msg,customClass:'default-div',type:"success"});}else if(response===true){}else{swal({title:"",text:"Failed to publish",customClass:'default-div',type:"error"});}
if(type==="reply"){var caja_comentarios=$('#caja-comentario-'+pks);$(caja_comentarios).find('.message-reply').val('');$(caja_comentarios).fadeOut();}else if(type==="publication"){$('#message-photo').val('');}},error:function(data,textStatus){var response=$.parseJSON(data.responseText);var error_msg=response.error[0];var type_error=response.type_error;if(type_error==='incorrent_data'){swal({title:'¡Ups!',text:error_msg,customClass:'default-div',type:"error"});}else{swal({title:'¡Ups!',text:'Revisa el contenido de tu mensaje',customClass:'default-div',type:"error"});}}}).done(function(){})}
function AJAX_delete_publication_gallery(caja_publicacion){var id_pub=$(caja_publicacion).attr('id').split('-')[1];var id_user=$(caja_publicacion).data('id');var data={userprofile_id:id_user,publication_id:id_pub,'csrfmiddlewaretoken':csrftoken};$.ajax({url:'/publication_p/delete/',type:'POST',dataType:'json',data:data,success:function(data){if(data==true){$(caja_publicacion).fadeToggle("fast");}else{swal({title:"Fail",customClass:'default-div',text:"Failed to delete publish.",type:"error"});}},error:function(rs,e){}});}
function AJAX_add_like_gallery(caja_publicacion,heart,type){var id_pub;if(type.localeCompare("publication")==0){id_pub=$(caja_publicacion).attr('id').split('-')[1];}else if(type.localeCompare("timeline")==0){id_pub=$(caja_publicacion).attr('data-publication');}
var id_user=$(caja_publicacion).attr('data-id');var data={userprofile_id:id_user,publication_id:id_pub,'csrfmiddlewaretoken':csrftoken};$.ajax({url:'/publication_p/add_like/',type:'POST',dataType:'json',data:data,success:function(data){var response=data.response;var status=data.statuslike;var numLikes=$(heart).find('.like-value');var countLikes=numLikes.text();if(response==true){if(!countLikes||(Math.floor(countLikes)==countLikes&&$.isNumeric(countLikes))){if(status==1){$(heart).css('color','#f06292');countLikes++;}else if(status==2){$(heart).css('color','#555');countLikes--;}else if(status==3){$(heart).css('color','#f06292');var hatesObj=$(heart).prev();var hates=hatesObj.find(".hate-value");var countHates=hates.text();countHates--;if(countHates<=0){hates.text('');}else
hates.text(countHates);$(hatesObj).css('color','#555');countLikes++;}
if(countLikes<=0){numLikes.text('');}else{numLikes.text(countLikes);}}else{if(status==1)
$(heart).css('color','#f06292');if(status==2)
$(heart).css('color','#555');}}else{swal({title:":-(",text:"¡No puedes dar me gusta a este comentario!",timer:4000,customClass:'default-div',animation:"slide-from-bottom",showConfirmButton:false,type:"error"});}},error:function(rs,e){}});}
function AJAX_add_hate_gallery(caja_publicacion,heart,type){var id_pub;if(type.localeCompare("publication")==0){id_pub=$(caja_publicacion).attr('id').split('-')[1];}else if(type.localeCompare("timeline")==0){id_pub=$(caja_publicacion).attr('data-publication');}
var id_user=$(caja_publicacion).attr('id');var data={userprofile_id:id_user,publication_id:id_pub,'csrfmiddlewaretoken':csrftoken};$.ajax({url:'/publication_p/add_hate/',type:'POST',dataType:'json',data:data,success:function(data){var statusOk=1;var statusNo=2;var statusInLike=3;var response=data.response;var status=data.statuslike;var numHates=$(heart).find(".hate-value");var countHates=numHates.text();if(response==true){if(!countHates||(Math.floor(countHates)==countHates&&$.isNumeric(countHates))){if(status===statusOk){$(heart).css('color','#ba68c8');countHates++;}else if(status===statusNo){$(heart).css('color','#555');countHates--;}else if(status===statusInLike){$(heart).css('color','#ba68c8');countHates++;var likesObj=$(heart).next();var likes=likesObj.find(".like-value");var countLikes=likes.text();countLikes--;if(countLikes<=0){likes.text('');}else
likes.text(countLikes);$(likesObj).css('color','#555');}
if(countHates<=0){numHates.text("");}else{numHates.text(countHates);}}else{if(status===statusOk){$(heart).css('color','#ba68c8');}else if(status===statusNo){$(heart).css('color','#555');}}}else{swal({title:":-(",text:"¡No puedes dar no me gusta a este comentario!",timer:4000,customClass:'default-div',animation:"slide-from-bottom",showConfirmButton:false,type:"error"});}},error:function(rs,e){}});}
function AJAX_add_timeline_gallery(pub_id,tag,data_pub){var data={'publication_id':pub_id,'content':data_pub,'csrfmiddlewaretoken':csrftoken};var shared_tag=$(tag).find('.fa-quote-right');var count_shared=$(shared_tag).text();count_shared=count_shared.replace(/ /g,'');$.ajax({url:'/publication_p/share/publication/',type:'POST',dataType:'json',data:data,success:function(data){var response=data.response;if(response==true){var status=data.status;if(status==1){if(!count_shared||(Math.floor(count_shared)==count_shared&&$.isNumeric(count_shared))){count_shared++;if(count_shared>0){$(shared_tag).text(" "+count_shared)}else{$(shared_tag).text(" ");}}
$(tag).attr("class","remove-timeline");$(tag).css('color','#bbdefb');$('#share-publication-wrapper').hide();}else if(status==2){if(!count_shared||(Math.floor(count_shared)==count_shared&&$.isNumeric(count_shared))){count_shared--;if(count_shared>0){$(shared_tag).text(" "+count_shared)}else{$(shared_tag).text(" ");}}
$(tag).attr("class","add-timeline");$(tag).css('color','#555');}}else{swal({title:"Fail",customClass:'default-div',text:"Failed to add to timeline.",type:"error"});}},error:function(rs,e){}});}
function AJAX_edit_publication_gallery(pub,content){var data={'id':pub,'content':content,'csrfmiddlewaretoken':csrftoken};$.ajax({url:'/publication_p/edit/',type:'POST',dataType:'json',data:data,success:function(data){var response=data.data;console.log(data.data);if(response==true){$('#p_author-controls-'+pub).fadeToggle("fast");}else{swal({title:"Fail",customClass:'default-div',text:"Failed to edit publish.",type:"error"});}},error:function(rs,e){}});}
function add_loaded_publication_gallery(pub,data,btn,is_skyline){var publications=JSON.parse(data);if(!publications||publications.length<=0){if(is_skyline)
$(btn).remove();return;}
var existing=$('#pub-'+pub);var pub_to_add;if(existing.length&&!is_skyline){var children_list=$(existing).find('.children').first();if(!children_list.length){children_list=$(existing).find('.wrapper-reply').after('<ul class="children"></ul>');}
var content="";var i;for(i=0;i<publications.length;i++){pub_to_add=$('pub-'+publications[i].id);if(undefined!==pub_to_add&&pub_to_add.length)continue;content='<div class="row">';content+='<div class="col s12">';if(publications[i].level>0&&publications[i].level<3){content+=' <div class="col s12 wrapper" id="pub-'+publications[i].id+'" data-id="'+publications[i].user_id+'" style="min-width: 98% !important;">';}else
content+=' <div class=\"col s12 wrapper\" id="pub-'+publications[i].id+'" data-id="'+publications[i].user_id+'">';content+="            <div class=\"box\">";content+='            <span id="check-'+publications[i].id+'" class=\"top-options zoom-pub tooltipped\" data-position=\"bottom\" data-delay=\"50\" data-tooltip=\"Ver conversación completa\"><i class=\"fa fa-plus-square-o\" aria-hidden=\"true\"><\/i><\/span>';if(publications[i].user_id==publications[i].p_author_id&&(publications[i].event_type==1||publications[i].event_type==3)){content+='            <span data-id="'+publications[i].id+'" class=\"top-options edit-comment tooltipped\" data-position=\"bottom\" data-delay=\"50\" data-tooltip=\"Editar comentario\"><i class=\"fa fa-pencil\" aria-hidden=\"true\"><\/i><\/span>';}
content+='<div class="row">';content+="                <div class=\"articulo col s12\">";content+='<div class="row">';if(publications[i].user_id==publications[i].p_author_id){content+='      <div class="image col l1 m2 s2" style="box-shadow: 0 1px 5px rgba(129, 199, 132, 1);">';}else{content+="      <div class=\"image col l1 m2 s2\">";}
content+='        <div class="usr-img img-responsive">'+publications[i].author_avatar+'</div>';content+="      </div>";content+='<div class="col l10 m12 s9">';content+='                  <h2 class="h22"><a href="/profile/'+publications[i].author_username+'" >@'+publications[i].author_username+'</a>';if(publications[i].parent){content+='<span class="chip">';content+=publications[i].parent_avatar;content+='<i class="fa fa-reply"></i> <a href="/profile/'+publications[i].parent_author+'">@'+publications[i].parent_author+'</a>';content+='</span>';}
content+='</h2>';content+='                    <p class="blue-text text-darken-2 pub-created">'+publications[i].created+'<\/p><br>';content+='<div class="row publication-content">';content+="                  <div class=\"parrafo comment\">";content+='                      <div class="wrp-comment">'+publications[i].content+'<\/div>';content+="                  </div>";content+='                    <div class="show-more" id="show-comment-'+publications[i].id+'">';content+="                        <a href=\"#\">+ Mostrar más<\/a>";content+="                    </div>";content+="                    </div>";if(publications[i].extra_content){if(publications[i].extra_content_video){content+=publications[i].extra_content_video;}else{content+='<div class="card small">';content+='<div class="card-image">';if(publications[i].extra_content_image){content+='<img src="'+publications[i].extra_content_image+'">';}else{content+='<img src="/static/dist/img/nuevo_back.png">';}
content+='<span class="card-title white-text">'+publications[i].extra_content_title+'</span>';content+='</div>';content+='<div class="card-content">';content+='<p>'+publications[i].extra_content_description+'</p>';content+='</div>';content+='<div class="card-action">';content+='<a href="'+publications[i].extra_content_url+'">Ver</a>';content+='</div></div>';}}
if(typeof(publications[i].images)!=='undefined'&&publications[i].images.length>0){content+='<div class="row images">';for(var image=0;image<publications[i].images.length;image++){content+='<div class="col s4 z-depth-2">';content+=publications[i].images[image];content+="                    </div>";}
content+="                    </div>";}
if(typeof(publications[i].videos)!=='undefined'&&publications[i].videos.length>0){content+='<div class="row videos">';for(var video=0;video<publications[i].videos.length;video++){content+='<div class="col s4 z-depth-2 center">';content+='<video class="responsive-video" controls loop><source src="'+publications[i].videos[video]+'" type="video/mp4"></video>';content+="                    </div>";}
content+="                    </div>";}
content+="                    </div>";content+="                    </div>";content+="                    </div>";content+="                    </div>";content+='<div class="row">';content+='<div class="divider"></div>';content+="                <div class=\"options_comentarios\">";content+="                    <ul class=\"opciones\">";if(publications[i].user_id==publications[i].board_photo_id||publications[i].user_id==publications[i].p_author_id){content+="                             <li class=\"trash-comment\" title=\"Borrar comentario\"><i class=\"fa fa-trash\"><\/i><\/li>";}
if(publications[i].user_hate===true)
content+='                            <li title="No me gusta" class="hate-comment" style="color: rgb(186, 104, 200)">';else
content+='                            <li title="No me gusta" class="hate-comment">';content+='                                <i class="fa fa-angle-down" aria-hidden="true"></i>';content+='                                <i class="fa hate-value">'+(publications[i].hates>0?publications[i].hates:'')+'</i>';content+="                            </li>";if(publications[i].user_like===true)
content+='                        <li title="¡Me gusta!" class="like-comment" style="color: rgb(240, 98, 146)"><i class="fa fa-angle-up" aria-hidden="true"></i><i class="fa like-value">'+(publications[i].likes>0?publications[i].likes:'')+'</i></li>';else
content+='                        <li title="¡Me gusta!" class="like-comment"><i class="fa fa-angle-up" aria-hidden="true"></i><i class="fa like-value">'+(publications[i].likes>0?publications[i].likes:'')+'</i></li>';if(publications[i].user_shared===true)
content+='                       <li title="Añadir a mi skyline" data-id="'+publications[i].id+'" class="remove-timeline" style="color: rgb(187, 222, 251)"><i class="fa fa-quote-right" aria-hidden="true"> '+(publications[i].shares>0?publications[i].shares:'')+'</i></li>';else
content+='                       <li title="Añadir a mi skyline" data-id="'+publications[i].id+'" class="add-timeline"><i class="fa fa-quote-right" aria-hidden="true"> '+(publications[i].shares>0?publications[i].shares:'')+'</i></li>';content+='                       <li title="Responder" class="reply-comment"><i class="fa fa-reply" id="reply-caja-comentario-'+publications[i].id+'"><\/i><\/li>';content+="                    </ul>";content+="                </div>";content+="                </div>";content+="    </div>";if(publications[i].user_id==publications[i].p_author_id){content+='<div data-user-id="'+publications[i].p_author_id+'" id="author-controls-'+publications[i].id+'" class="author-controls">';content+='<div class="row">';content+='<div class="col s12">';content+='<form method="post" accept-charset="utf-8">';content+='<input type="hidden" name="csrfmiddlewaretoken" value="'+publications[i].token+'">';content+='<div class="row">';content+='<div class="input-field col s12">';content+='<i class="material-icons prefix">create</i>';content+='<textarea class="materialize-textarea" placeholder="Escribe el contenido del nuevo mensaje" id="id_caption-'+publications[i].id+'" cols="40" maxlength="500" name="content" rows="10" required="required" style="height: 10.9969px;"></textarea>';content+='<label for="id_caption-'+publications[i].id+'">Editar comentario</label></div>';content+='<div class="row">';content+='<button data-id="'+publications[i].id+'" class="waves-effect waves-light btn blue darken-1 right edit-comment-btn" type="button">Editar<i class="material-icons right">mode_edit</i></button>';content+='</div></div></form></div></div></div>';}
content+='<div class="wrapper-reply">';content+='<div class="hidden" id="caja-comentario-'+publications[i].id+'">';content+='<form class="reply-form" action="" method="post">';content+='<input type="hidden" name="csrfmiddlewaretoken" value="'+publications[i].token+'">';content+='<input id="id_author" name="p_author" type="hidden" value="'+publications[i].user_id+'">';content+='<input id="id_board_photo" name="board_photo" type="hidden" value="'+publications[i].board_photo_id+'">';content+='<input id="id_parent" name="parent" type="hidden" value="'+publications[i].id+'">';content+='<div class="row">';content+='<div class="col s12">';content+='<div class="row">';content+='<div class="input-field col s12">';content+='<textarea class="materialize-textarea message-reply" id="message-reply-'+publications[i].id+'" cols="40" maxlength="500" name="content" placeholder="Responder a @'+publications[i].author_username+'" rows="10" required=""></textarea>';content+='<label for="message-reply-'+publications[i].id+'">Escribe tu mensaje aqui...</label>';content+='</div>';content+='<div class="file-field input-field col s12">';content+='<div class="btn">';content+='<span>Imágenes</span>';content+='<input id="id_image_reply" name="image" type="file" multiple>';content+='</div>';content+='<div class="file-path-wrapper">';content+='<input class="file-path validate" type="text" placeholder="Upload one or more files">';content+='</div></div></div></div></div>';content+='<button type="button" id="reply-'+publications[i].id+'" class="waves-effect waves-light btn right blue enviar">Enviar<i class="material-icons right">send</i></button>';content+='</form></div></div>';if(publications[i].descendants>0){content+='<div class="row">';content+='<div class="col s12">';content+='<a class="waves-effect waves-light btn-large blue darken-1 white-text center load_more_descendants" href="#" data-id="'+publications[i].id+'"><i class=" material-icons left">expand_more</i>Cargar comentarios <span class="child_count">('+publications[i].descendants+')</span></a>';content+='<div>';content+='<div class="progress load_publications_descendants" style="display: none;">';content+='<div class="indeterminate blue darken-1"></div></div>';content+='</div></div></div>';}
content+="    </div></div></div>";$(content).appendTo(children_list).hide().fadeIn(250);}
var child_count=$(btn).find('.child_count');var result_child_count=parseInt($(child_count).html(),10)-publications.length;if(result_child_count>0)
$(child_count).html(result_child_count);else
$(btn).remove();}}
function AJAX_load_publications_gallery(loader,btn){if(!$(btn)||!($(btn).length))return;var pub=$(btn).attr("data-id");var data={'id':pub,'csrfmiddlewaretoken':csrftoken};$.ajax({url:'/publication_p/load_publications/',type:'POST',dataType:'json',data:data,success:function(data){var response=data.response;if(response==true){add_loaded_publication_gallery(pub,data.pubs,btn,true);}else{swal({title:"Fail",customClass:'default-div',text:"Failed to load more publications.",type:"error"});}},complete:function(){$(loader).fadeOut();},error:function(rs,e){}});}
function AJAX_load_descendants_gallery(pub,loader,last_pub,btn){var data={'id':pub,'last_pub':last_pub,'csrfmiddlewaretoken':csrftoken};$.ajax({url:'/publication_p/load_descendants/',type:'POST',dataType:'json',data:data,success:function(data){var response=data.response;if(response==true){add_loaded_publication_gallery(pub,data.pubs,btn,false);}else{swal({title:"Fail",customClass:'default-div',text:"Failed to load more publications.",type:"error"});}},complete:function(){$(loader).fadeOut();},error:function(rs,e){}});};var max_height_comment=60;var UTILS=UTILS||(function(){var _args={};var _showLimitChar=90;return{init:function(args){_args=args;},conn_socket:function(){var ws_scheme=window.location.protocol=="https:"?"wss":"ws";var ws_path=ws_scheme+'://'+window.location.host+window.location.pathname+"stream/";console.log("Connecting to "+ws_path);var socket=new ReconnectingWebSocket(ws_path);socket.onmessage=function(message){console.log("Got message "+message.data);var data=JSON.parse(message.data);if(data.type==="pub"){var content="";content+='<div class="row">';content+='<div class="col s12">';if(data.level>0){content+=' <div class="col s12 wrapper" id="pub-'+data.id+'" data-id="'+_args+'" style="min-width: 98% !important; border-right: 3px solid #1e88e5;">';}else
content+=' <div class=\"col s12 wrapper\" id="pub-'+data.id+'" data-id="'+_args+'">';content+="            <div class=\"box\">";content+='            <span id="check-'+data.id+'" class=\"top-options zoom-pub tooltipped\" data-position=\"bottom\" data-delay=\"50\" data-tooltip=\"Ver conversación completa\"><i class=\"fa fa-plus-square-o\" aria-hidden=\"true\"><\/i><\/span>';if(_args==data.p_author_id&&(data.event_type==1||data.event_type==3)){content+='            <span data-id="'+data.id+'" id=\"edit-comment-content\" class=\"top-options edit-comment tooltipped\" data-position=\"bottom\" data-delay=\"50\" data-tooltip=\"Editar comentario\"><i class=\"fa fa-pencil\" aria-hidden=\"true\"><\/i><\/span>';}
content+='<div class="row">';content+="                <div class=\"articulo col s12\">";content+='<div class="row">';if(_args==data.p_author_id){1
content+="      <div class=\"image col l1 m2 s2\" style=\"box-shadow: 0 1px 5px rgba(129, 199, 132, 1);\">";}else{content+="      <div class=\"image col l1 m2 s2\">";}
content+='        <div class="usr-img img-responsive"><img src="'+data.avatar_path+'" alt="'+data.p_author_username+'" width="120" height="120"></div>';content+="      </div>";content+='<div class="col l10 m12 s9">';content+='                  <h2 class="h22"><a href="/profile/'+data.p_author_username+'" >@'+data.p_author_username+'</a>';if(data.parent){content+='<span class="chip">';content+='<img src="'+data.parent_avatar+'" alt="'+data.p_author_parent+'">';content+='<i class="fa fa-reply"></i> <a href="/profile/'+data.parent_author+'">@'+data.parent_author+'</a>';content+='</span>';}
content+='</h2>';content+='                    <p class="blue-text text-darken-2 pub-created">'+data.created+'<\/p><br>';content+='<div class="row publication-content">';content+="                  <div class=\"parrafo comment\">";content+='                      <div class="wrp-comment">'+data.content+'<\/div>';content+="                  </div>";content+='                    <div class="show-more" id="show-comment-'+data.id+'">';content+="                        <a href=\"#\">+ Mostrar más<\/a>";content+="                    </div>";content+="                    </div>";if(data.extra_content){if(data.extra_content_video){content+=data.extra_content_video;}else{content+='<div class="card small">';content+='<div class="card-image">';if(data.extra_content_image){content+='<img src="'+data.extra_content_image+'">';}else{content+='<img src="/static/dist/img/nuevo_back.png">';}
content+='<span class="card-title white-text">'+data.extra_content_title+'</span>';content+='</div>';content+='<div class="card-content">';content+='<p>'+data.extra_content_description+'</p>';content+='</div>';content+='<div class="card-action">';content+='<a href="'+data.extra_content_url+'">Ver</a>';content+='</div></div>';}}
if(data.images!==undefined&&data.images.length>0){content+='<div class="row images">';for(var image=0;image<data.images.length;image++){content+='<div class="col s4 z-depth-2">';content+='<img class="responsive-img" src="/media/'+data.images[image].image+'" alt="Imagen de: '+data.p_author_username+'" title="Imagen de: '+data.p_author_username+'">';content+="                    </div>";}
content+="                    </div>";}
content+="                    </div>";content+="                    </div>";content+="                    </div>";content+="                    </div>";content+='<div class="row">';content+='<div class="divider"></div>';content+="                <div class=\"options_comentarios\">";content+="                    <ul class=\"opciones\">";if(_args==data.photo_owner||data.p_author_id==_args){content+="                             <li class=\"trash-comment\" title=\"Borrar comentario\"><i class=\"fa fa-trash\"><\/i><\/li>";}
content+="                            <li title=\"No me gusta\" class=\"hate-comment\">";content+='                                <i class="fa fa-angle-down" aria-hidden="true"></i>';content+='                                <i class="fa hate-value"></i>';content+="                            </li>";content+='                        <li title="¡Me gusta!" class="like-comment"><i class="fa fa-angle-up" aria-hidden="true"></i><i class="fa like-value"></i></li>';content+='                       <li title=\"Añadir a mi skyline\" data-id="'+data.id+'" class=\"add-timeline\"><i class=\"fa fa-quote-right\" aria-hidden=\"true\"> <\/i><\/li>';content+='                       <li title="Responder" class="reply-comment"><i class="fa fa-reply" id="reply-caja-comentario-'+data.id+'"><\/i><\/li>';content+="                    </ul>";content+="                </div>";content+="                </div>";content+="    </div>";if(_args==data.p_author_id){content+='<div data-user-id="'+data.p_author_id+'" id="p_author-controls-'+data.id+'" class="p_author-controls">';content+='<div class="row">';content+='<div class="col s12">';content+='<form method="post" accept-charset="utf-8">';content+='<input type="hidden" name="csrfmiddlewaretoken" value="'+data.token+'">';content+='<div class="row">';content+='<div class="input-field col s12">';content+='<i class="material-icons prefix">create</i>';content+='<textarea class="materialize-textarea" placeholder="Escribe el contenido del nuevo mensaje" id="id_caption-'+data.id+'" cols="40" maxlength="500" name="content" rows="10" required="required" style="height: 10.9969px;"></textarea>';content+='<label for="id_caption-'+data.id+'">Editar comentario</label></div>';content+='<div class="row">';content+='<button data-id="'+data.id+'" class="waves-effect waves-light btn blue darken-1 right edit-comment-btn" type="button">Editar<i class="material-icons right">mode_edit</i></button>';content+='</div></div></form></div></div></div>';}
content+='<div class="wrapper-reply">';content+='<div class="hidden" id="caja-comentario-'+data.id+'">';content+='<form class="reply-form" action="" method="post">';content+='<input type="hidden" name="csrfmiddlewaretoken" value="'+data.token+'">';content+='<input name="p_author" type="hidden" value="'+_args+'">';content+='<input name="board_photo" type="hidden" value="'+data.board_photo_id+'">';content+='<input name="parent" type="hidden" value="'+data.id+'">';content+='<div class="row">';content+='<div class="col s12">';content+='<div class="row">';content+='<div class="input-field col s12">';content+='<textarea class="materialize-textarea message-reply" id="message-reply-'+data.id+'" cols="40" maxlength="500" name="content" placeholder="Responder a @'+data.p_author_username+'" rows="10" required=""></textarea>';content+='<label for="message-reply-'+data.id+'">Escribe tu mensaje aqui...</label>';content+='</div>';content+='<div class="file-field input-field col s12">';content+='<div class="btn">';content+='<span>Imágenes</span>';content+='<input id="id_image_reply" name="image" type="file" multiple>';content+='</div>';content+='<div class="file-path-wrapper">';content+='<input class="file-path validate" type="text" placeholder="Upload one or more files">';content+='</div></div></div></div></div>';content+='<button type="button" id="reply-'+data.id+'" class="waves-effect waves-light btn right blue enviar">Enviar<i class="material-icons right">send</i></button>';content+='</form></div></div>';content+="    </div></div></div>";var existing=$('#pub-'+data.id);var no_comments=$('#without-comments');if(existing.length){existing.find('.pub-created').first().text(data.created);existing.find('.wrp-comment').first().text(data.content);}else{var parent=$('#pub-'+data.parent);if(parent.length){if(data.level==1||data.level==2){var children_list=$(parent).find('.children').first();if(!children_list.length){children_list=$(parent).find('.wrapper-reply').after('<ul class="children"></ul>');}
$(children_list).prepend(content);}else{$(parent).closest('.row').after(content);}}else $("#messages-wrapper").prepend(content);}
var show=$('div#pub-'+data.id+'').find('#show-comment-'+data.id+'');if($(no_comments).is(':visible')){$(no_comments).fadeOut();}
var wrapper_content=$('#pub-'+data.id+'').find('.wrp-comment');if($(wrapper_content).height()>max_height_comment){$(wrapper_content).css('height','2.6em');}else{$(show).css('display','none');}}else if(data.type==="video"){var existing_pub=$('#pub-'+data.id);if(existing_pub.length){var card_content=$(existing_pub).find('.publication-content');var videos=$(existing_pub).find('.videos');if(videos.length){$(videos).append('<div class="col s4"><video class="responsive-video" controls loop><source src="/media/'+data.video+'" type="video/mp4"></video></div>');}else{var images=$(existing_pub).find('.images');if(images.length){$(images).after('<div class="row videos"><div class="col s4"><video class="responsive-video" controls loop><source src="/media/'+data.video+'" type="video/mp4"></video></div></div>');}
$(card_content).after('<div class="row videos"><div class="col s4"><video class="responsive-video" controls loop><source src="/media/'+data.video+'" type="video/mp4"></video></div></div>');}}}else{var content="";content+="                <div class=\"wrapper-reply\">";content+="";content+="";content+="                <div class=\"comment-reply\">";content+='                <div class=\"avatar-reply\"><img src="'+data.avatar_path+'" alt="'+data.p_author_username+'" width="120" height="120"><\/div>';content+="                    <div class=\"author-reply\">";content+='                      <a href="/profile/'+data.p_author_username+'">'+data.p_author_username+'</a>';content+='                      <i class="reply-created">'+data.created+'<\/i>';content+="                    </div>";content+='                      <div class="content-reply">'+data.content+'</div>';content+="                </div>";content+="";content+="                </div>";content+="    </div>";var pub=$('#pub-'+data.parent);$(pub).append(content);}};if(socket.readyState==WebSocket.OPEN)socket.onopen();socket.onclose=function(){console.log("No connected.");};}};}());;!function(a,b){"function"==typeof define&&define.amd?define([],b):"undefined"!=typeof module&&module.exports?module.exports=b():a.ReconnectingWebSocket=b()}(this,function(){function a(b,c,d){function l(a,b){var c=document.createEvent("CustomEvent");return c.initCustomEvent(a,!1,!1,b),c}var e={debug:!1,automaticOpen:!0,reconnectInterval:1e3,maxReconnectInterval:3e4,reconnectDecay:1.5,timeoutInterval:2e3};d||(d={});for(var f in e)this[f]="undefined"!=typeof d[f]?d[f]:e[f];this.url=b,this.reconnectAttempts=0,this.readyState=WebSocket.CONNECTING,this.protocol=null;var h,g=this,i=!1,j=!1,k=document.createElement("div");k.addEventListener("open",function(a){g.onopen(a)}),k.addEventListener("close",function(a){g.onclose(a)}),k.addEventListener("connecting",function(a){g.onconnecting(a)}),k.addEventListener("message",function(a){g.onmessage(a)}),k.addEventListener("error",function(a){g.onerror(a)}),this.addEventListener=k.addEventListener.bind(k),this.removeEventListener=k.removeEventListener.bind(k),this.dispatchEvent=k.dispatchEvent.bind(k),this.open=function(b){h=new WebSocket(g.url,c||[]),b||k.dispatchEvent(l("connecting")),(g.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","attempt-connect",g.url);var d=h,e=setTimeout(function(){(g.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","connection-timeout",g.url),j=!0,d.close(),j=!1},g.timeoutInterval);h.onopen=function(){clearTimeout(e),(g.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","onopen",g.url),g.protocol=h.protocol,g.readyState=WebSocket.OPEN,g.reconnectAttempts=0;var d=l("open");d.isReconnect=b,b=!1,k.dispatchEvent(d)},h.onclose=function(c){if(clearTimeout(e),h=null,i)g.readyState=WebSocket.CLOSED,k.dispatchEvent(l("close"));else{g.readyState=WebSocket.CONNECTING;var d=l("connecting");d.code=c.code,d.reason=c.reason,d.wasClean=c.wasClean,k.dispatchEvent(d),b||j||((g.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","onclose",g.url),k.dispatchEvent(l("close")));var e=g.reconnectInterval*Math.pow(g.reconnectDecay,g.reconnectAttempts);setTimeout(function(){g.reconnectAttempts++,g.open(!0)},e>g.maxReconnectInterval?g.maxReconnectInterval:e)}},h.onmessage=function(b){(g.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","onmessage",g.url,b.data);var c=l("message");c.data=b.data,k.dispatchEvent(c)},h.onerror=function(b){(g.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","onerror",g.url,b),k.dispatchEvent(l("error"))}},1==this.automaticOpen&&this.open(!1),this.send=function(b){if(h)return(g.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","send",g.url,b),h.send(b);throw"INVALID_STATE_ERR : Pausing to reconnect websocket"},this.close=function(a,b){"undefined"==typeof a&&(a=1e3),i=!0,h&&h.close(a,b)},this.refresh=function(){h&&h.close()}}return a.prototype.onopen=function(){},a.prototype.onclose=function(){},a.prototype.onconnecting=function(){},a.prototype.onmessage=function(){},a.prototype.onerror=function(){},a.debugAll=!1,a.CONNECTING=WebSocket.CONNECTING,a.OPEN=WebSocket.OPEN,a.CLOSING=WebSocket.CLOSING,a.CLOSED=WebSocket.CLOSED,a});