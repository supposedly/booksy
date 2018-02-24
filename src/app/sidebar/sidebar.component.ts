import { Component, OnInit, Input } from '@angular/core';
import { DomSanitizer } from '@angular/platform-browser';

import { ButtonService } from '../button.service';

import { SideButton } from '../classes';
import { Globals } from '../globals';

@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.css']
})
export class SidebarComponent /*implements OnInit*/ {
  public san;
  buttons: SideButton[] = null;
  
  constructor(
    public globals: Globals,
    private buttonService: ButtonService,
    private sanitizer: DomSanitizer
  ) {
      this.san = sanitizer.bypassSecurityTrustStyle; // so I can use it from the template
  }
  
  @Input() uID: string;
  
  ngOnChanges() {
    this.getButtons();
  }
  
  /*
  ngOnInit() {
    this.getButtons();
  }
  */
  
  getButtons(): void {
    this.buttonService.getSidebarButtons(this.uID)
      .subscribe(resp => this.buttons = resp.buttons)
  }

}
