from flask import Blueprint, render_template, request, url_for, redirect, flash
from core.redis import rds
from core.security import session_required


notes = Blueprint('notes', __name__,
                    template_folder='templates')


@notes.route('/notes')
@session_required
def view_notes():
    my_param_note = request.args.get('id')
    my_main_note = None

    # Searchs
    my_notes = my_param_note
    
        # Nothing found
    my_notes = rds.get_json('notes')
    if not my_param_note and my_notes:
        # Show first result
        my_main_note = my_notes[0]
    else:
    # Show first note
        try:
            my_note_temp = rds.get_json('notes')
            for note in my_note_temp:
                if note['title'] == my_param_note:
                    my_main_note = note
                    break
            # Is there any note in the database?
        except:
            flash('No such note was written','error')
        
    # Data for template
    data = dict()
    data['notes'] = my_notes
    data['main_note'] = my_main_note

    return render_template('items/dashboard.html', data=data)

@notes.route('/newnote')
@session_required
def new():
    return render_template('items/new.html')


@notes.route('/newnote/save', methods=['POST'])
@session_required
def save_note():
    myNote = {'title':request.form['title'].strip(),'text': request.form['text'].strip()}
    # Create
    tmp = rds.get_json('notes')
    if tmp:
        tmp.insert(0,myNote)
    else:
        tmp = [myNote]
    rds.store_json('notes',tmp)
    return redirect(url_for('notes.view_notes'))


@notes.route('/editnote')
@session_required
def edit(data=None):
    my_main_note = None
    id = request.args.get('id')
    my_note_temp = rds.get_json('notes')
    for note in my_note_temp:
        if note['title'] == id:
            my_main_note = note
            break

    data= {}
    data['main_note'] = my_main_note
    return render_template('items/edit.html', data=data)


@notes.route('/edit_note', methods=['POST'])
@session_required
def edit_note(data=None):
    if request.form['id']:
        # Update
        my_notes = rds.get_json('notes')
        for i in range(0,len(my_notes)):
            if my_notes[i]['title'] == request.form['id']:
                my_notes[i] = {'title':request.form['title'].strip(),'text': request.form['text'].strip()}
                break

        #my_note.title = request.form['title']
        #my_note.text = request.form['text']
        rds.store_json('notes',my_notes)

    return redirect(url_for('notes.view_notes'))


@notes.route('/deletenote')
@session_required
def delete():
    id = request.args.get('id')
    tmp = rds.get_json('notes')
    my_note = {}
    for i in tmp:
        if i['title'] == id:
            my_note = i 
            break
    data = dict()
    data['main_note'] = my_note

    return render_template('items/delete.html', data=data)


@notes.route('/delete_note')
@session_required
def delete_note():
    id = request.args.get('id')
    # Delete
    tmp = rds.get_json('notes')
    for i in range(0,len(tmp)):
        print(i)
        if tmp[i]['title'] == id:
            del tmp[i] 
            break
    if tmp:
        rds.store_json('notes',tmp)
    else:
        rds.delete('notes')

    return redirect(url_for('notes.view_notes', id=id))