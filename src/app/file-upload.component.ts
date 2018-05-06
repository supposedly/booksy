import { Component, ElementRef, Input, ViewChild } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { asElementData } from '@angular/core/src/view';

// Modified slightly from https://stackoverflow.com/a/39862337/
// by user "Brother Woodrow".

@Component({
    // tslint:disable-next-line:component-selector
    selector: 'file-upload',
    template: `
      <input type="file" (change)="upload()" [multiple]="multiple" #fileInput>
      <whatsthis ident=12></whatsthis><label>{{msg}}</label>
    `
})
export class FileUploadComponent {
    @Input() multiple = false;
    @Input('url') fileUploadURL: string;
    @ViewChild('fileInput') inputEl: ElementRef;
    msg: string;
    
    constructor(private http: HttpClient) {}
    
    upload() {
        const inputEl: HTMLInputElement = this.inputEl.nativeElement;
        const fileCount: number = inputEl.files.length;
        const formData = new FormData();
        if (fileCount > 0) { // a file was selected
            for (let i = 0; i < fileCount; i++) {
                formData.append('file[]', inputEl.files.item(i));
            }
            this.http.post(this.fileUploadURL, formData)
              .subscribe(resp => this.msg = 'Uploaded successfully.', err => this.msg = err.error ? err.error : 'Error.');
        }
    }
}
