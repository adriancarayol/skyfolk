;var countFriendList=1;var flag_reply=false;var max_height_comment=60;$(document).ready(function(){var tab_comentarios=$('#tab-comentarios');var tab_amigos=$('#tab-amigos');var wrapper_shared_pub=$('#share-publication-wrapper');$(tab_comentarios).find('.wrapper').each(function(){var comment=$(this).find('.wrp-comment');var show=$(this).find('.show-more a');if($(comment).height()>max_height_comment){$(show).show();$(comment).css('height','2.6em');}else{}});$(tab_comentarios).on('click','.show-more a',function(){var $this=$(this);var $content=$this.parent().prev("div.comment").find(".wrp-comment");var linkText=$this.text().toUpperCase();if(linkText==="+ MOSTRAR MÁS"){linkText="- Mostrar menos";$content.css('height','auto');}else{linkText="+ Mostrar más";$content.css('height','2.6em');}
$this.text(linkText);return false;});$('.fa-paw').on('click',function(){$(".info-paw").show();});$('.info-trof').on('click',function(){$(".trofeos").show();});$('.info-groups').on('click',function(){$(".grupos").show();});$('#close-trofeos').on('click',function(){$(".trofeos").hide();});$('#close-grupos').on('click',function(){$(".grupos").hide();});$('#configurationOnProfile').on('click',function(){var _ventana_pin=$('.ventana-pin');if($(_ventana_pin).is(':visible')){$('html, body').removeClass('body-inConf');$(_ventana_pin).fadeOut("fast");}else{$('html, body').addClass('body-inConf');$(_ventana_pin).fadeIn("fast");}});$(tab_comentarios).on('click','.options_comentarios .fa-reply',function(){var id_=$(this).attr("id").slice(6);$("#"+id_).slideToggle("fast");});$(tab_comentarios).on('click','.edit-comment',function(){var id=$(this).attr('data-id');$("#author-controls-"+id).slideToggle("fast");});$(tab_comentarios).on('click','.edit-comment-btn',function(event){event.preventDefault();var id=$(this).attr('data-id');var content=$(this).closest('#author-controls-'+id).find('#id_caption-'+id).val();AJAX_edit_publication(id,content);});function replyComment(caja_pub){var id_comment=$(caja_pub).attr('id').split('-')[1];var commentReply=document.getElementById('actual-'+id_comment);$(commentReply).toggleClass("reply-actual-message-show");}
$(tab_comentarios).on('click','.wrapper .zoom-pub',function(){var caja_pub=$(this).closest('.wrapper');expandComment(caja_pub);});function expandComment(caja_pub){var id_pub=$(caja_pub).attr('id').split('-')[1];window.location.href='/publication/'+id_pub;}
$('.cerrar_ampliado').on('click',function(){var expand=$(this).closest('.ampliado');closeExpand(expand);});function closeExpand(expand){var c=$(expand).attr('id').split('-')[1];var toClose=document.getElementById('expand-'+c);$(toClose).hide();}
$(tab_comentarios).on('click','.options_comentarios .fa-trash',function(){var caja_publicacion=$(this).closest('.wrapper');swal({title:"Are you sure?",text:"You will not be able to recover this publication!",type:"warning",animation:"slide-from-top",showConfirmButton:true,showCancelButton:true,confirmButtonColor:"#DD6B55",confirmButtonText:"Yes, delete it!",cancelButtonText:"No God, please no!",closeOnConfirm:true},function(isConfirm){if(isConfirm){AJAX_delete_publication(caja_publicacion);}});});$(this).on('click','.options_comentarios .add-timeline',function(e){var tag=$(this);$(wrapper_shared_pub).attr('data-id',$(tag).data('id'))
$(wrapper_shared_pub).show();});$(wrapper_shared_pub).find('#share_publication_form').on('submit',function(event){event.preventDefault();var content=$(wrapper_shared_pub).find('#shared_comment_content').val();var pub_id=$(wrapper_shared_pub).attr('data-id');var tag=$('#pub-'+pub_id).find('.add-timeline').first();AJAX_add_timeline(pub_id,tag,content);});$('#close_share_publication').click(function(){$(wrapper_shared_pub).hide();});$(this).on('click','.options_comentarios .remove-timeline',function(){var caja_publicacion=$(this).closest('.wrapper');var tag=this;AJAX_add_timeline($(caja_publicacion).attr('id').split('-')[1],tag,null);});$(this).on('click','.options_comentarios .like-comment',function(){var caja_publicacion=$(this).closest('.wrapper');var heart=this;AJAX_add_like(caja_publicacion,heart,"publication");});$(document).on('click','.options_comentarios .hate-comment',function(){var caja_publicacion=$(this).closest('.wrapper');var heart=this;AJAX_add_hate(caja_publicacion,heart,"publication");});$("#li-tab-amigos").click(function(){$(tab_amigos).css({"overflow":"auto"});});$("#li-tab-comentarios").click(function(){$(tab_comentarios).css({"overflow":"auto"});});$("#li-tab-timeline").click(function(){$('#tab-timeline').css({"overflow":"auto"});});$('#personal-card-info').find('#bloq-user').on('click',function(){var obj=document.getElementById('info-user-name-profile'),username=obj.getAttribute('data-id'),buttonBan=$(this);swal({title:"Bloquear a "+username,text:username+" no podrá seguirte, enviarte mensajes ni ver tu contenido.",type:"warning",customClass:'default-div',animation:"slide-from-top",showConfirmButton:true,showCancelButton:true,confirmButtonColor:"#DD6B55",confirmButtonText:"Bloquear",cancelButtonText:"Cancelar",closeOnConfirm:true},function(isConfirm){if(isConfirm){AJAX_bloq_user(buttonBan);}});});$(this).click(function(event){var _personal_card_info=$('#personal-card-info');if(!$(event.target).closest('#personal-card-info').length){if(!$(event.target).closest('.fa-paw').length){if($(_personal_card_info).is(":visible")){$(_personal_card_info).hide();}}}});$(tab_comentarios).on('click','.load_more_publications',function(e){e.preventDefault();var loader=$(this).next().find('.load_publications_descendants');var pub_id=$(this).data('id');var page=$('.page_for_'+pub_id).last().val();if(typeof page==='undefined')
page=1;AJAX_load_publications(pub_id,loader,page,this);});});function AJAX_likeprofile(status){if(status=="noabort")$.ajax({type:"POST",url:"/like_profile/",data:{'slug':$("#profileId").html(),'csrfmiddlewaretoken':csrftoken},dataType:"json",success:function(response){var _likes=$('#likes').find('strong');if(response=="like"){$("#ilike_profile").css('color','#ec407a');$(_likes).html(parseInt($(_likes).html())+1);}else if(response=="nolike"){$("#ilike_profile").css('color','#46494c');if($(_likes).html()>0){$(_likes).html(parseInt($(_likes).html())-1);}}else if(response=="blocked"){swal({title:"Vaya... algo no está bien.",customClass:'default-div',text:"Si quieres dar un like, antes debes desbloquear este perfil.",timer:4000,showConfirmButton:true,type:"error"});}else{console.log("...");}},error:function(rs,e){}});else if(status=="anonymous"){swal({title:"¡Ups!",text:"Debe estar registrado",customClass:'default-div'});}}
function AJAX_load_publications(pub,loader,page,btn){$.ajax({url:'/publication/load/more/?pubid='+pub+'&page='+page,type:'GET',beforeSend:function(){$(loader).fadeIn();},success:function(data){var $existing=$('#pub-'+pub);var $children_list=$existing.find('.children').first();if(!$children_list.length){$children_list=$existing.find('.wrapper-reply').after('<ul class="children"></ul>');}
$children_list.append(data);var $child_count=$(btn).find('.child_count');var $result_child_count=parseInt($child_count.html(),10)-$('.childs_for_'+pub).last().val();if($result_child_count>0)
$($child_count).html($result_child_count);else
$(btn).remove();},complete:function(){$(loader).fadeOut();},error:function(rs,e){console.log(e);}});}
function AJAX_edit_publication(pub,content){var data={'id':pub,'content':content,'csrfmiddlewaretoken':csrftoken};$.ajax({url:'/publication/edit/',type:'POST',dataType:'json',data:data,success:function(data){var response=data.data;console.log(data.data);if(response==true){$('#author-controls-'+pub).fadeToggle("fast");}else{swal({title:"Fail",customClass:'default-div',text:"Failed to edit publish.",type:"error"});}},error:function(rs,e){}});}
function AJAX_delete_publication(caja_publicacion){var id_pub=$(caja_publicacion).attr('id').split('-')[1];var id_user=$(caja_publicacion).attr('data-id');var data={userprofile_id:id_user,publication_id:id_pub,'csrfmiddlewaretoken':csrftoken};$.ajax({url:'/publication/delete/',type:'POST',dataType:'json',data:data,success:function(data){if(data.response==true){$(caja_publicacion).fadeToggle("fast");if(data.shared_pub_id){var shared_btn=$('#share-'+data.shared_pub_id);var shared_btn_child=shared_btn.children();var countShares=shared_btn_child.text();if(!countShares||(Math.floor(countShares)==countShares&&$.isNumeric(countShares))){countShares--;countShares>0?shared_btn_child(countShares):shared_btn_child.text('');}
shared_btn.attr('class','add-timeline');shared_btn.css('color','#555');}}else{swal({title:"Fail",customClass:'default-div',text:"Failed to delete publish.",type:"error"});}},error:function(rs,e){}});}
function AJAX_add_like(caja_publicacion,heart,type){var id_pub;if(type.localeCompare("publication")==0){id_pub=$(caja_publicacion).attr('id').split('-')[1];}else if(type.localeCompare("timeline")==0){id_pub=$(caja_publicacion).attr('data-publication');}
var id_user=$(caja_publicacion).attr('data-id');var data={userprofile_id:id_user,publication_id:id_pub,'csrfmiddlewaretoken':csrftoken};$.ajax({url:'/publication/add_like/',type:'POST',dataType:'json',data:data,success:function(data){var response=data.response;var status=data.statuslike;var numLikes=$(heart).find('.like-value');var countLikes=numLikes.text();if(response==true){if(!countLikes||(Math.floor(countLikes)==countLikes&&$.isNumeric(countLikes))){if(status==1){$(heart).css('color','#f06292');countLikes++;}else if(status==2){$(heart).css('color','#555');countLikes--;}else if(status==3){$(heart).css('color','#f06292');var hatesObj=$(heart).prev();var hates=hatesObj.find(".hate-value");var countHates=hates.text();countHates--;if(countHates<=0){hates.text('');}else
hates.text(countHates);$(hatesObj).css('color','#555');countLikes++;}
if(countLikes<=0){numLikes.text('');}else{numLikes.text(countLikes);}}else{if(status==1)
$(heart).css('color','#f06292');if(status==2)
$(heart).css('color','#555');}}else{swal({title:":-(",text:"¡No puedes dar me gusta a este comentario!",timer:4000,customClass:'default-div',animation:"slide-from-bottom",showConfirmButton:false,type:"error"});}},error:function(rs,e){}});}
function AJAX_add_hate(caja_publicacion,heart,type){var id_pub;if(type.localeCompare("publication")==0){id_pub=$(caja_publicacion).attr('id').split('-')[1];}else if(type.localeCompare("timeline")==0){id_pub=$(caja_publicacion).attr('data-publication');}
var id_user=$(caja_publicacion).attr('id');var data={userprofile_id:id_user,publication_id:id_pub,'csrfmiddlewaretoken':csrftoken};$.ajax({url:'/publication/add_hate/',type:'POST',dataType:'json',data:data,success:function(data){var statusOk=1;var statusNo=2;var statusInLike=3;var response=data.response;var status=data.statuslike;var numHates=$(heart).find(".hate-value");var countHates=numHates.text();if(response==true){if(!countHates||(Math.floor(countHates)==countHates&&$.isNumeric(countHates))){if(status===statusOk){$(heart).css('color','#ba68c8');countHates++;}else if(status===statusNo){$(heart).css('color','#555');countHates--;}else if(status===statusInLike){$(heart).css('color','#ba68c8');countHates++;var likesObj=$(heart).next();var likes=likesObj.find(".like-value");var countLikes=likes.text();countLikes--;if(countLikes<=0){likes.text('');}else
likes.text(countLikes);$(likesObj).css('color','#555');}
if(countHates<=0){numHates.text("");}else{numHates.text(countHates);}}else{if(status===statusOk){$(heart).css('color','#ba68c8');}else if(status===statusNo){$(heart).css('color','#555');}}}else{swal({title:":-(",text:"¡No puedes dar no me gusta a este comentario!",timer:4000,customClass:'default-div',animation:"slide-from-bottom",showConfirmButton:false,type:"error"});}},error:function(rs,e){}});}
function AJAX_add_timeline(pub_id,tag,data_pub){var data={'publication_id':pub_id,'content':data_pub,'csrfmiddlewaretoken':csrftoken};var shared_tag=$(tag).find('.fa-quote-right');var count_shared=$(shared_tag).text();count_shared=count_shared.replace(/ /g,'');$.ajax({url:'/publication/share/publication/',type:'POST',dataType:'json',data:data,success:function(data){var response=data.response;if(response==true){var status=data.status;if(status==1){if(!count_shared||(Math.floor(count_shared)==count_shared&&$.isNumeric(count_shared))){count_shared++;if(count_shared>0){$(shared_tag).text(" "+count_shared)}else{$(shared_tag).text(" ");}}
$(tag).attr("class","remove-timeline");$(tag).css('color','#bbdefb');$('#share-publication-wrapper').hide();}else if(status==2){if(!count_shared||(Math.floor(count_shared)==count_shared&&$.isNumeric(count_shared))){count_shared--;if(count_shared>0){$(shared_tag).text(" "+count_shared)}else{$(shared_tag).text(" ");}}
$(tag).attr("class","add-timeline");$(tag).css('color','#555');}}else{swal({title:"Fail",customClass:'default-div',text:"Failed to add to timeline.",type:"error"});}},error:function(rs,e){}});}
function AJAX_bloq_user(buttonBan){var id_user=$("#profileId").html();$.ajax({type:'POST',url:'/bloq_user/',data:{'id_user':id_user,'csrfmiddlewaretoken':csrftoken},dataType:"json",success:function(data){if(data.response==true){$(buttonBan).css('color','#FF6347');if(data.status=="none"||data.status=="isfollow"){$('#addfriend').replaceWith('<span class="fa fa-ban" id="bloq-user-span" title="Bloqueado" onclick="AJAX_remove_bloq();">'+' '+'</span>');}else if(data.status=="inprogress"){$('#follow_request').replaceWith('<span class="fa fa-ban" id="bloq-user-span" title="Bloqueado" onclick="AJAX_remove_bloq();">'+' '+'</span>');}
if(data.haslike=="liked"){$("#ilike_profile").css('color','#46494c');var obj_likes=document.getElementById('likes');if($(obj_likes).find("strong").html()>0){$(obj_likes).find("strong").html(parseInt($(obj_likes).find("strong").html())-1);}}}else{swal({title:"Tenemos un problema...",customClass:'default-div',text:"Hubo un problema con su petición.",timer:4000,showConfirmButton:true});}},error:function(rs,e){}});}
function AJAX_remove_bloq(){$.ajax({type:'POST',url:'/remove_blocked/',data:{'slug':$("#profileId").html(),'csrfmiddlewaretoken':csrftoken},dataType:"json",success:function(response){if(response==true){$('#bloq-user-span').replaceWith('<span id="addfriend" class="fa fa-plus" title="Seguir" style="color:#555 !important;" onclick=AJAX_requestfriend("noabort");>'+' '+'</span>');$('#bloq-user').css('color','#555');}else{swal({title:"Tenemos un problema...",customClass:'default-div',text:"Hubo un problema con su petición.",timer:4000,showConfirmButton:true});}},error:function(rs,e){}});};(function(a){a.easytabs=function(j,e){var f=this,q=a(j),i={animate:true,panelActiveClass:"active",tabActiveClass:"active",defaultTab:"li:first-child",animationSpeed:"normal",tabs:"> ul > li",updateHash:true,cycle:false,collapsible:false,collapsedClass:"collapsed",collapsedByDefault:true,uiTabs:false,transitionIn:"fadeIn",transitionOut:"fadeOut",transitionInEasing:"swing",transitionOutEasing:"swing",transitionCollapse:"slideUp",transitionUncollapse:"slideDown",transitionCollapseEasing:"swing",transitionUncollapseEasing:"swing",containerClass:"",tabsClass:"",tabClass:"",panelClass:"",cache:true,event:"click",panelContext:q},h,l,v,m,d,t={fast:200,normal:400,slow:600},r;f.init=function(){f.settings=r=a.extend({},i,e);r.bind_str=r.event+".easytabs";if(r.uiTabs){r.tabActiveClass="ui-tabs-selected";r.containerClass="ui-tabs ui-widget ui-widget-content ui-corner-all";r.tabsClass="ui-tabs-nav ui-helper-reset ui-helper-clearfix ui-widget-header ui-corner-all";r.tabClass="ui-state-default ui-corner-top";r.panelClass="ui-tabs-panel ui-widget-content ui-corner-bottom"}if(r.collapsible&&e.defaultTab!==undefined&&e.collpasedByDefault===undefined){r.collapsedByDefault=false}if(typeof(r.animationSpeed)==="string"){r.animationSpeed=t[r.animationSpeed]}a("a.anchor").remove().prependTo("body");q.data("easytabs",{});f.setTransitions();f.getTabs();b();g();w();n();c();q.attr("data-easytabs",true)};f.setTransitions=function(){v=(r.animate)?{show:r.transitionIn,hide:r.transitionOut,speed:r.animationSpeed,collapse:r.transitionCollapse,uncollapse:r.transitionUncollapse,halfSpeed:r.animationSpeed/2}:{show:"show",hide:"hide",speed:0,collapse:"hide",uncollapse:"show",halfSpeed:0}};f.getTabs=function(){var x;f.tabs=q.find(r.tabs),f.panels=a(),f.tabs.each(function(){var A=a(this),z=A.children("a"),y=A.children("a").data("target");A.data("easytabs",{});if(y!==undefined&&y!==null){A.data("easytabs").ajax=z.attr("href")}else{y=z.attr("href")}y=y.match(/#([^\?]+)/)[1];x=r.panelContext.find("#"+y);if(x.length){x.data("easytabs",{position:x.css("position"),visibility:x.css("visibility")});x.not(r.panelActiveClass).hide();f.panels=f.panels.add(x);A.data("easytabs").panel=x}else{f.tabs=f.tabs.not(A);if("console"in window){console.warn("Warning: tab without matching panel for selector '#"+y+"' removed from set")}}})};f.selectTab=function(x,C){var y=window.location,B=y.hash.match(/^[^\?]*/)[0],z=x.parent().data("easytabs").panel,A=x.parent().data("easytabs").ajax;if(r.collapsible&&!d&&(x.hasClass(r.tabActiveClass)||x.hasClass(r.collapsedClass))){f.toggleTabCollapse(x,z,A,C)}else{if(!x.hasClass(r.tabActiveClass)||!z.hasClass(r.panelActiveClass)){o(x,z,A,C)}else{if(!r.cache){o(x,z,A,C)}}}};f.toggleTabCollapse=function(x,y,z,A){f.panels.stop(true,true);if(u(q,"easytabs:before",[x,y,r])){f.tabs.filter("."+r.tabActiveClass).removeClass(r.tabActiveClass).children().removeClass(r.tabActiveClass);if(x.hasClass(r.collapsedClass)){if(z&&(!r.cache||!x.parent().data("easytabs").cached)){q.trigger("easytabs:ajax:beforeSend",[x,y]);y.load(z,function(C,B,D){x.parent().data("easytabs").cached=true;q.trigger("easytabs:ajax:complete",[x,y,C,B,D])})}x.parent().removeClass(r.collapsedClass).addClass(r.tabActiveClass).children().removeClass(r.collapsedClass).addClass(r.tabActiveClass);y.addClass(r.panelActiveClass)[v.uncollapse](v.speed,r.transitionUncollapseEasing,function(){q.trigger("easytabs:midTransition",[x,y,r]);if(typeof A=="function"){A()}})}else{x.addClass(r.collapsedClass).parent().addClass(r.collapsedClass);y.removeClass(r.panelActiveClass)[v.collapse](v.speed,r.transitionCollapseEasing,function(){q.trigger("easytabs:midTransition",[x,y,r]);if(typeof A=="function"){A()}})}}};f.matchTab=function(x){return f.tabs.find("[href='"+x+"'],[data-target='"+x+"']").first()};f.matchInPanel=function(x){return(x&&f.validId(x)?f.panels.filter(":has("+x+")").first():[])};f.validId=function(x){return x.substr(1).match(/^[A-Za-z]+[A-Za-z0-9\-_:\.].$/)};f.selectTabFromHashChange=function(){var y=window.location.hash.match(/^[^\?]*/)[0],x=f.matchTab(y),z;if(r.updateHash){if(x.length){d=true;f.selectTab(x)}else{z=f.matchInPanel(y);if(z.length){y="#"+z.attr("id");x=f.matchTab(y);d=true;f.selectTab(x)}else{if(!h.hasClass(r.tabActiveClass)&&!r.cycle){if(y===""||f.matchTab(m).length||q.closest(y).length){d=true;f.selectTab(l)}}}}}};f.cycleTabs=function(x){if(r.cycle){x=x%f.tabs.length;$tab=a(f.tabs[x]).children("a").first();d=true;f.selectTab($tab,function(){setTimeout(function(){f.cycleTabs(x+1)},r.cycle)})}};f.publicMethods={select:function(x){var y;if((y=f.tabs.filter(x)).length===0){if((y=f.tabs.find("a[href='"+x+"']")).length===0){if((y=f.tabs.find("a"+x)).length===0){if((y=f.tabs.find("[data-target='"+x+"']")).length===0){if((y=f.tabs.find("a[href$='"+x+"']")).length===0){a.error("Tab '"+x+"' does not exist in tab set")}}}}}else{y=y.children("a").first()}f.selectTab(y)}};var u=function(A,x,z){var y=a.Event(x);A.trigger(y,z);return y.result!==false};var b=function(){q.addClass(r.containerClass);f.tabs.parent().addClass(r.tabsClass);f.tabs.addClass(r.tabClass);f.panels.addClass(r.panelClass)};var g=function(){var y=window.location.hash.match(/^[^\?]*/)[0],x=f.matchTab(y).parent(),z;if(x.length===1){h=x;r.cycle=false}else{z=f.matchInPanel(y);if(z.length){y="#"+z.attr("id");h=f.matchTab(y).parent()}else{h=f.tabs.parent().find(r.defaultTab);if(h.length===0){a.error("The specified default tab ('"+r.defaultTab+"') could not be found in the tab set ('"+r.tabs+"') out of "+f.tabs.length+" tabs.")}}}l=h.children("a").first();p(x)};var p=function(z){var y,x;if(r.collapsible&&z.length===0&&r.collapsedByDefault){h.addClass(r.collapsedClass).children().addClass(r.collapsedClass)}else{y=a(h.data("easytabs").panel);x=h.data("easytabs").ajax;if(x&&(!r.cache||!h.data("easytabs").cached)){q.trigger("easytabs:ajax:beforeSend",[l,y]);y.load(x,function(B,A,C){h.data("easytabs").cached=true;q.trigger("easytabs:ajax:complete",[l,y,B,A,C])})}h.data("easytabs").panel.show().addClass(r.panelActiveClass);h.addClass(r.tabActiveClass).children().addClass(r.tabActiveClass)}q.trigger("easytabs:initialised",[l,y])};var w=function(){f.tabs.children("a").bind(r.bind_str,function(x){r.cycle=false;d=false;f.selectTab(a(this));x.preventDefault?x.preventDefault():x.returnValue=false})};var o=function(z,D,E,H){f.panels.stop(true,true);if(u(q,"easytabs:before",[z,D,r])){var A=f.panels.filter(":visible"),y=D.parent(),F,x,C,G,B=window.location.hash.match(/^[^\?]*/)[0];if(r.animate){F=s(D);x=A.length?k(A):0;C=F-x}m=B;G=function(){q.trigger("easytabs:midTransition",[z,D,r]);if(r.animate&&r.transitionIn=="fadeIn"){if(C<0){y.animate({height:y.height()+C},v.halfSpeed).css({"min-height":""})}}if(r.updateHash&&!d){window.location.hash="#"+D.attr("id")}else{d=false}D[v.show](v.speed,r.transitionInEasing,function(){y.css({height:"","min-height":""});q.trigger("easytabs:after",[z,D,r]);if(typeof H=="function"){H()}})};if(E&&(!r.cache||!z.parent().data("easytabs").cached)){q.trigger("easytabs:ajax:beforeSend",[z,D]);D.load(E,function(J,I,K){z.parent().data("easytabs").cached=true;q.trigger("easytabs:ajax:complete",[z,D,J,I,K])})}if(r.animate&&r.transitionOut=="fadeOut"){if(C>0){y.animate({height:(y.height()+C)},v.halfSpeed)}else{y.css({"min-height":y.height()})}}f.tabs.filter("."+r.tabActiveClass).removeClass(r.tabActiveClass).children().removeClass(r.tabActiveClass);f.tabs.filter("."+r.collapsedClass).removeClass(r.collapsedClass).children().removeClass(r.collapsedClass);z.parent().addClass(r.tabActiveClass).children().addClass(r.tabActiveClass);f.panels.filter("."+r.panelActiveClass).removeClass(r.panelActiveClass);D.addClass(r.panelActiveClass);if(A.length){A[v.hide](v.speed,r.transitionOutEasing,G)}else{D[v.uncollapse](v.speed,r.transitionUncollapseEasing,G)}}};var s=function(z){if(z.data("easytabs")&&z.data("easytabs").lastHeight){return z.data("easytabs").lastHeight}var B=z.css("display"),y,x;try{y=a("<div></div>",{position:"absolute",visibility:"hidden",overflow:"hidden"})}catch(A){y=a("<div></div>",{visibility:"hidden",overflow:"hidden"})}x=z.wrap(y).css({position:"relative",visibility:"hidden",display:"block"}).outerHeight();z.unwrap();z.css({position:z.data("easytabs").position,visibility:z.data("easytabs").visibility,display:B});z.data("easytabs").lastHeight=x;return x};var k=function(y){var x=y.outerHeight();if(y.data("easytabs")){y.data("easytabs").lastHeight=x}else{y.data("easytabs",{lastHeight:x})}return x};var n=function(){if(typeof a(window).hashchange==="function"){a(window).hashchange(function(){f.selectTabFromHashChange()})}else{if(a.address&&typeof a.address.change==="function"){a.address.change(function(){f.selectTabFromHashChange()})}}};var c=function(){var x;if(r.cycle){x=f.tabs.index(h);setTimeout(function(){f.cycleTabs(x+1)},r.cycle)}};f.init()};a.fn.easytabs=function(c){var b=arguments;return this.each(function(){var e=a(this),d=e.data("easytabs");if(undefined===d){d=new a.easytabs(this,c);e.data("easytabs",d)}if(d.publicMethods[c]){return d.publicMethods[c](Array.prototype.slice.call(b,1))}})}})(jQuery);;(function($,e,b){var c="hashchange",h=document,f,g=$.event.special,i=h.documentMode,d="on"+c in e&&(i===b||i>7);function a(j){j=j||location.href;return"#"+j.replace(/^[^#]*#?(.*)$/,"$1")}$.fn[c]=function(j){return j?this.bind(c,j):this.trigger(c)};$.fn[c].delay=50;g[c]=$.extend(g[c],{setup:function(){if(d){return false}$(f.start)},teardown:function(){if(d){return false}$(f.stop)}});f=(function(){var j={},p,m=a(),k=function(q){return q},l=k,o=k;j.start=function(){p||n()};j.stop=function(){p&&clearTimeout(p);p=b};function n(){var r=a(),q=o(m);if(r!==m){l(m=r,q);$(e).trigger(c)}else{if(q!==m){location.href=location.href.replace(/#.*/,"")+q}}p=setTimeout(n,$.fn[c].delay)}$.browser.msie&&!d&&(function(){var q,r;j.start=function(){if(!q){r=$.fn[c].src;r=r&&r+a();q=$('<iframe tabindex="-1" title="empty"/>').hide().one("load",function(){r||l(a());n()}).attr("src",r||"javascript:0").insertAfter("body")[0].contentWindow;h.onpropertychange=function(){try{if(event.propertyName==="title"){q.document.title=h.title}}catch(s){}}}};j.stop=k;o=function(){return a(q.location.href)};l=function(v,s){var u=q.document,t=$.fn[c].domain;if(v!==s){u.title=h.title;u.open();t&&u.write('<script>document.domain="'+t+'"<\/script>');u.close();q.location.hash=v}}})();return j})()})(jQuery,this);