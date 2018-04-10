import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-generic-header',
  templateUrl: './generic-header.component.html',
  styleUrls: ['./generic-header.component.css']
})
export class GenericHeaderComponent {
  @Input() buttons: any;
  @Input() inbetween: string;
}
