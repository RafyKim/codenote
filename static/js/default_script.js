
function add_note(csrfmiddlewaretoken){

    var name = $("#note_name").val();
    var content = CKEDITOR.instances.note_content.getData();
    var isNotPublic = $("#isNotPublic").is(":checked");

    var topic = '';
    $( "#topic input[type='hidden']" ).each(function() {
        topic += $(this).val() + ':$&*:';
    });


    $.ajax({
        type: "POST",
        url: "/ajax/note/add/",
        data: {name: name, content: content, isNotPublic: isNotPublic, topic: topic, csrfmiddlewaretoken: csrfmiddlewaretoken },
        dataType: "json",
        success: function(msg) {
            window.location.replace("/note/read/"+msg.id);
        },
        error: function(){
        }
    });

}


function del_note(note_id, csrfmiddlewaretoken){

    $.ajax({
        type: "POST",
        url: "/ajax/note/del/",
        data: {note_id: note_id, csrfmiddlewaretoken: csrfmiddlewaretoken },
        dataType: "json",
        success: function(msg) {
            window.location.replace("/user");
        },
        error: function(){
        }
    });

}



function edit_note(note_id, csrfmiddlewaretoken){

    var name = $("#note_name").val();
    var content = CKEDITOR.instances.note_content.getData();
    var isNotPublic = $("#isNotPublic").is(":checked");

    var topic = '';
    $( "#topic input[type='hidden']" ).each(function() {
        topic += $(this).val() + ':$&*:';
    });

    $.ajax({
        type: "POST",
        url: "/ajax/note/edit/",
        data: {note_id: note_id, name: name, content: content, isNotPublic: isNotPublic, topic: topic, csrfmiddlewaretoken: csrfmiddlewaretoken },
        dataType: "json",
        success: function(msg) {
            window.location.replace("/note/read/"+note_id);
        },
        error: function(){
        }
    });

}


function decollect_note(note_id, csrfmiddlewaretoken){

    $.ajax({
        type: "POST",
        url: "/ajax/note/decollect/",
        data: {note_id: note_id, csrfmiddlewaretoken: csrfmiddlewaretoken },
        dataType: "json",
        success: function(msg) {
            $("#bt_collect").addClass('btn-default');
            $("#bt_collect").removeClass('btn-info');
            $("#bt_collect").attr('onclick', $("#bt_collect").attr('onclick').replace('decollect','collect'));
            var cnt_col = $("#cnt_col").html();
            cnt_col--;
            $("#cnt_col").html(cnt_col);
        },
        error: function(){
        }
    });

}

function collect_note(note_id, csrfmiddlewaretoken){

    $.ajax({
        type: "POST",
        url: "/ajax/note/collect/",
        data: {note_id: note_id, csrfmiddlewaretoken: csrfmiddlewaretoken },
        dataType: "json",
        success: function(msg) {
            $("#bt_collect").addClass('btn-info');
            $("#bt_collect").removeClass('btn-default');
            $("#bt_collect").attr('onclick', $("#bt_collect").attr('onclick').replace('collect','decollect'));
            var cnt_col = $("#cnt_col").html();
            cnt_col++;
            $("#cnt_col").html(cnt_col);

        },
        error: function(){
        }
    });

}


function add_cmt(csrfmiddlewaretoken) {


    var note_id = $("#note_id").val();
    var content = $("#cmt_content").val();

	$.ajax({
		type: "POST",
		url: "/ajax/cmt/add/",
		data: {note_id: note_id, content: content, csrfmiddlewaretoken: csrfmiddlewaretoken },
//		dataType: "json",
		success: function(msg) {
            $("#cmt_list").prepend(msg);
            var cnt_cmt = $("#cnt_cmt").html();
            cnt_cmt++;
            $("#cnt_cmt").html(cnt_cmt);
		},
	    error: function(){
	    }
	});

}


function del_cmt(cmt_id, csrfmiddlewaretoken){

    $.ajax({
        type: "POST",
        url: "/ajax/cmt/del/",
        data: {cmt_id: cmt_id, csrfmiddlewaretoken: csrfmiddlewaretoken },
        dataType: "json",
        success: function(msg) {
            $("#comment"+cmt_id).remove();
            var cnt_cmt = $("#cnt_cmt").html();
            cnt_cmt--;
            $("#cnt_cmt").html(cnt_cmt);
        },
        error: function(){
        }
    });

}

