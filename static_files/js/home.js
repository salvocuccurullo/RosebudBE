$( document ).ready(function() {

	var base_url = "https://www.salvocuccurullo.com/icarusi_covers/poster/";


	function showPoster(titleName, posterName) {
          var poster = base_url + posterName
                title = titleName;

           $('#imagepreview').attr('src', poster); // here asign the image to the modal when the user click the enlarge link
           $('#myModalLabel').html(title); // here asign the image to the modal when the user click the enlarge link
           $('#imagemodal').modal('show'); // imagemodal is the id attribute assigned to the bootstrap modal, then i use the show function

	}
		
        $(".myitem").on("click", function() {
	   var poster = base_url + this.getAttribute("poster")
		title = this.getAttribute("title");

           $('#imagepreview').attr('src', poster); // here asign the image to the modal when the user click the enlarge link
           $('#myModalLabel').html(title); // here asign the image to the modal when the user click the enlarge link
           $('#imagemodal').modal('show'); // imagemodal is the id attribute assigned to the bootstrap modal, then i use the show function
        });

	var mTable = $('#moviesTable').DataTable({
		"columnDefs": [
		    {
			"targets": [ 0,3,4,6,7,8,10,11 ],
			"visible": false,
			"searchable": false
		    },
		    {
		    "targets": -1,
		    "data": null,
		    "defaultContent": '<img src="/static/images/icons/picture_icon.png" class="align-self-center mr-3 float-right myitem" style="width:25px"/>'
		},
		{
		    "targets": 2,
		    "data": 'media',
		    "sortable": true,
		    "render": function (data, type, row) {
			    return '<img src="/static/images/icons/' + data+ '-icon.png" class="align-self-center mr-3" style="width:25px"/>'
		    }
		}
			
		]	
	});
	$('#serieesTable').DataTable();


	$('#moviesTable tbody').on( 'click', 'img', function () {
	        var data = mTable.row( $(this).parents('tr') ).data();
        	showPoster(data[1], data[11]);
    	} );

});

