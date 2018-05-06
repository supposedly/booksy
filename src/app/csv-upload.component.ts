import { Component, ElementRef, Input, ViewChild } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { asElementData } from '@angular/core/src/view';

// Modified slightly from https://stackoverflow.com/a/39862337/
// by user "Brother Woodrow".

@Component({
    // tslint:disable-next-line:component-selector
    selector: 'member-csv-upload',
    template: `
      <input type="file" (change)="upload()" #fileInput>
      <whatsthis ident=12></whatsthis><label>{{msg}}</label>
    `
})
export class CSVUploadComponent {
    @Input() rID;  // int? string?
    @Input('url') fileUploadURL: string;
    @ViewChild('fileInput') inputEl: ElementRef;
    msg: string;
    
    constructor(private http: HttpClient) {}
    
    upload() {
        const inputEl: HTMLInputElement = this.inputEl.nativeElement;
        const formData = new FormData();
        formData.append('csv', inputEl.files[0]);
        formData.append('rid', this.rID);
        this.http.post(this.fileUploadURL, formData)
          .subscribe(resp => this.msg = 'Members added successfully.', err => this.msg = err.error ? err.error : 'Error.');
        this.msg = 'Uploading...';
    }
}
