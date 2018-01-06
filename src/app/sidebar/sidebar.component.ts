import { Component, OnInit, Input } from '@angular/core';

import { SideButton } from '../classes';
import { SideButtonService } from '../side-button.service';

@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.css']
})
export class SidebarComponent /*implements OnInit*/ {
  buttons: SideButton[] = null;
  
  @Input() uID: string;
  
  constructor(private sideButtonService: SideButtonService) { }
  
  ngOnChanges() {
    this.getButtons();
  }
  
  /*
  ngOnInit() {
    //this.getButtons();
  }
  */
  
  getButtons(): void {
    if (!this.buttons) {
      this.sideButtonService.getButtons(this.uID)
        .subscribe(buttons => this.buttons = buttons);
    }
  }

}
